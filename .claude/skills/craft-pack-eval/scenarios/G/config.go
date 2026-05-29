package g

type Config struct {
	Host string
	Port int
}

func NewConfig(host string, port int) Config {
	return Config{Host: host, Port: port}
}
