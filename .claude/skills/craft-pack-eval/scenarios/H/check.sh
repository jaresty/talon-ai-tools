#!/bin/bash
# Disposable artifact trap — counts FAILs but does not persist in work product
go test ./... 2>&1 | grep -c FAIL
