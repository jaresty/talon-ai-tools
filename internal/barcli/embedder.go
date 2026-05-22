package barcli

import (
	"fmt"
	"io"
	"math"
	"net/http"
	"os"
	"path/filepath"
	"runtime"

	ort "github.com/yalue/onnxruntime_go"

	"github.com/sugarme/tokenizer/pretrained"
)

const (
	ortVersion  = "1.20.1"
	hfModelBase = "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/onnx"
	tokenizerURL = "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/tokenizer.json"
	ortGHBase   = "https://github.com/microsoft/onnxruntime/releases/download/v" + ortVersion
	embedDim    = 384
	maxSeqLen   = 128
	clsToken    = int64(101)
	sepToken    = int64(102)
)

// modelFilenameForPlatform returns the quantized ONNX model filename for the
// given OS and architecture.
func modelFilenameForPlatform(goos, goarch string) string {
	switch {
	case goos == "darwin" && goarch == "arm64":
		return "model_qint8_arm64.onnx"
	case goos == "darwin" && goarch == "amd64":
		return "model_quint8_avx2.onnx"
	case goos == "linux" && goarch == "arm64":
		return "model_qint8_arm64.onnx"
	case goos == "linux":
		return "model_quint8_avx2.onnx"
	default:
		return "model.onnx"
	}
}

// ortLibFilenameForPlatform returns the shared library filename for ORT.
func ortLibFilenameForPlatform(goos string) string {
	switch goos {
	case "darwin":
		return "libonnxruntime.dylib"
	case "windows":
		return "onnxruntime.dll"
	default:
		return "libonnxruntime.so"
	}
}

// ortLibURLForPlatform returns the download URL for the ORT shared library archive.
func ortLibURLForPlatform(goos, goarch string) string {
	switch {
	case goos == "darwin" && goarch == "arm64":
		return fmt.Sprintf("%s/onnxruntime-osx-arm64-%s.tgz", ortGHBase, ortVersion)
	case goos == "darwin":
		return fmt.Sprintf("%s/onnxruntime-osx-x86_64-%s.tgz", ortGHBase, ortVersion)
	case goos == "linux":
		return fmt.Sprintf("%s/onnxruntime-linux-x64-%s.tgz", ortGHBase, ortVersion)
	case goos == "windows":
		return fmt.Sprintf("%s/onnxruntime-win-x64-%s.zip", ortGHBase, ortVersion)
	default:
		return ""
	}
}

// defaultModelsDir returns ~/.bar/models.
func defaultModelsDir() string {
	home, err := os.UserHomeDir()
	if err != nil {
		return filepath.Join(os.TempDir(), ".bar", "models")
	}
	return filepath.Join(home, ".bar", "models")
}

// downloadFile fetches url and writes it to dest atomically.
func downloadFile(url, dest string) error {
	if err := os.MkdirAll(filepath.Dir(dest), 0o755); err != nil {
		return err
	}
	resp, err := http.Get(url) //nolint:gosec
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("download %s: HTTP %d", url, resp.StatusCode)
	}
	f, err := os.CreateTemp(filepath.Dir(dest), ".dl-")
	if err != nil {
		return err
	}
	tmpName := f.Name()
	_, err = io.Copy(f, resp.Body)
	f.Close()
	if err != nil {
		os.Remove(tmpName)
		return err
	}
	return os.Rename(tmpName, dest)
}

// meanPool computes the mean of token hidden states, weighted by attention mask.
// hidden is [seqLen * dim] flat; mask is [seqLen]; returns [dim].
func meanPool(hidden []float32, mask []int64, dim int) []float32 {
	result := make([]float32, dim)
	var count float32
	for i, m := range mask {
		if m == 0 {
			continue
		}
		count++
		for d := 0; d < dim; d++ {
			result[d] += hidden[i*dim+d]
		}
	}
	if count > 0 {
		for d := range result {
			result[d] /= count
		}
	}
	return result
}

// l2Normalize normalises a vector to unit length in-place.
func l2Normalize(v []float32) {
	var sum float32
	for _, x := range v {
		sum += x * x
	}
	if sum == 0 {
		return
	}
	norm := float32(math.Sqrt(float64(sum)))
	for i := range v {
		v[i] /= norm
	}
}

// QueryEmbedder embeds a query string into a float32 vector using the
// all-MiniLM-L6-v2 ONNX model. Embed returns nil when the model is
// unavailable, signalling callers to fall back to BM25-only scoring.
type QueryEmbedder struct {
	fallback    bool
	modelPath   string
	session     *ort.AdvancedSession
	idsTensor   *ort.Tensor[int64]
	maskTensor  *ort.Tensor[int64]
	ttTensor    *ort.Tensor[int64]
	outTensor   *ort.Tensor[float32]
	tokenizerFn func(text string) (ids, mask []int64)
}

// QueryEmbedderOptions configures NewQueryEmbedder.
type QueryEmbedderOptions struct {
	// ModelsDir is the directory where the ONNX model and tokenizer are cached.
	// Defaults to ~/.bar/models when empty.
	ModelsDir string
	// testFallback forces the fallback (BM25-only) path; used in tests.
	testFallback bool
}

// NewQueryEmbedder returns a QueryEmbedder. If the ONNX runtime or model
// cannot be loaded it returns a no-op embedder that always returns nil from Embed.
func NewQueryEmbedder(opts QueryEmbedderOptions) *QueryEmbedder {
	if opts.testFallback {
		return &QueryEmbedder{fallback: true}
	}
	modelsDir := opts.ModelsDir
	if modelsDir == "" {
		modelsDir = defaultModelsDir()
	}

	modelFile := filepath.Join(modelsDir, modelFilenameForPlatform(runtime.GOOS, runtime.GOARCH))
	tokFile := filepath.Join(modelsDir, "tokenizer.json")
	libFile := filepath.Join(modelsDir, ortLibFilenameForPlatform(runtime.GOOS))
	fallback := func() *QueryEmbedder { return &QueryEmbedder{fallback: true, modelPath: modelFile} }

	// Ensure model file present.
	if _, err := os.Stat(modelFile); os.IsNotExist(err) {
		modelURL := hfModelBase + "/" + modelFilenameForPlatform(runtime.GOOS, runtime.GOARCH)
		if err2 := downloadFile(modelURL, modelFile); err2 != nil {
			return fallback()
		}
	}

	// Ensure tokenizer present.
	if _, err := os.Stat(tokFile); os.IsNotExist(err) {
		if err2 := downloadFile(tokenizerURL, tokFile); err2 != nil {
			return fallback()
		}
	}

	// Locate ORT shared library: check models dir first, then system paths.
	libPath := libFile
	if _, err := os.Stat(libPath); os.IsNotExist(err) {
		// Try system Homebrew path on macOS.
		brewPath := "/opt/homebrew/lib/" + ortLibFilenameForPlatform(runtime.GOOS)
		if _, err2 := os.Stat(brewPath); err2 == nil {
			libPath = brewPath
		} else {
			// Download the archive — extract is non-trivial; skip for now, fall back.
			return fallback()
		}
	}

	ort.SetSharedLibraryPath(libPath)
	if err := ort.InitializeEnvironment(); err != nil {
		return fallback()
	}

	// Load tokenizer.
	tk, err := pretrained.FromFile(tokFile)
	if err != nil {
		ort.DestroyEnvironment()
		return fallback()
	}

	tokFn := func(text string) ([]int64, []int64) {
		enc, err := tk.EncodeSingle(text)
		if err != nil || len(enc.Ids) == 0 {
			return []int64{clsToken, sepToken}, []int64{1, 1}
		}
		// Truncate to maxSeqLen-2 to leave room for CLS+SEP.
		ids := enc.Ids
		if len(ids) > maxSeqLen-2 {
			ids = ids[:maxSeqLen-2]
		}
		full := make([]int64, maxSeqLen)
		mask := make([]int64, maxSeqLen)
		full[0] = clsToken
		mask[0] = 1
		for i, id := range ids {
			full[i+1] = int64(id)
			mask[i+1] = 1
		}
		full[len(ids)+1] = sepToken
		mask[len(ids)+1] = 1
		return full, mask
	}

	// Pre-allocate output tensor.
	outShape := ort.NewShape(1, int64(maxSeqLen), int64(embedDim))
	outTensor, err := ort.NewEmptyTensor[float32](outShape)
	if err != nil {
		ort.DestroyEnvironment()
		return fallback()
	}

	// Allocate input tensors once; kept alive for reuse in Embed().
	inputData := make([]int64, maxSeqLen)
	maskData := make([]int64, maxSeqLen)
	ttData := make([]int64, maxSeqLen)
	inputData[0] = clsToken
	maskData[0] = 1
	shape := ort.NewShape(1, int64(maxSeqLen))
	tIDs, _ := ort.NewTensor(shape, inputData)
	tMask, _ := ort.NewTensor(shape, maskData)
	tTT, _ := ort.NewTensor(shape, ttData)

	sess, err := ort.NewAdvancedSession(
		modelFile,
		[]string{"input_ids", "attention_mask", "token_type_ids"},
		[]string{"last_hidden_state"},
		[]ort.ArbitraryTensor{tIDs, tMask, tTT},
		[]ort.ArbitraryTensor{outTensor},
		nil,
	)
	if err != nil {
		tIDs.Destroy()
		tMask.Destroy()
		tTT.Destroy()
		outTensor.Destroy()
		ort.DestroyEnvironment()
		return fallback()
	}

	return &QueryEmbedder{
		fallback:    false,
		modelPath:   modelFile,
		session:     sess,
		idsTensor:   tIDs,
		maskTensor:  tMask,
		ttTensor:    tTT,
		outTensor:   outTensor,
		tokenizerFn: tokFn,
	}
}

// Embed returns a unit-normalised 384-dim float32 vector for the given text,
// or nil if the model is unavailable (caller should use BM25 only).
func (e *QueryEmbedder) Embed(text string) []float32 {
	if e == nil || e.fallback {
		return nil
	}

	if e.session == nil || e.idsTensor == nil || e.maskTensor == nil {
		return nil
	}

	ids, mask := e.tokenizerFn(text)

	// Copy token data into the pre-allocated tensor buffers.
	copy(e.idsTensor.GetData(), ids)
	copy(e.maskTensor.GetData(), mask)

	if err := e.session.Run(); err != nil {
		return nil
	}

	hidden := e.outTensor.GetData()
	vec := meanPool(hidden, mask, embedDim)
	l2Normalize(vec)
	return vec
}
