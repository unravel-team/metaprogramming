package mathx

import (
	"testing"

	"pgregory.net/rapid"
)

func TestPropertyDoubling(t *testing.T) {
	rapid.Check(t, func(t *rapid.T) {
		value := rapid.IntRange(-1000000, 1000000).Draw(t, "value")
		if got := Example(value); got != value+value {
			t.Fatalf("Example(%d) = %d, want %d", value, got, value+value)
		}
	})
}
