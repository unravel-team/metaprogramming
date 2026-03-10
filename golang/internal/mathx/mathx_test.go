package mathx

import "testing"

func TestExample(t *testing.T) {
	if got := 1 + 1; got != 2 {
		t.Fatalf("got %d, want 2", got)
	}
}
