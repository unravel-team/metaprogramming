package mathx

import (
	"testing"

	"hegel.dev/go/hegel"
)

func TestPropertyDoubling(t *testing.T) {
	hegel.Test(t, func(t *hegel.T) {
		value := hegel.Draw(t, hegel.Integers(-1000000, 1000000))
		if got := Example(value); got != value+value {
			t.Fatalf("Example(%d) = %d, want %d", value, got, value+value)
		}
	})
}
