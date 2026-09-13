package mathx

import "testing"

func TestExample(t *testing.T) {
	for _, value := range []int{0, 2, -3} {
		if got := Example(value); got != value+value {
			t.Fatalf("Example(%d) = %d, want %d", value, got, value+value)
		}
	}
}
