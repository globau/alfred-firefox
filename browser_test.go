package main

import "testing"

func TestParseBrowserPath(t *testing.T) {
	for _, tt := range []struct {
		name string
		data string
		want string
	}{
		{"nightly", `"/Applications/Firefox Nightly.app"`, "/Applications/Firefox Nightly.app"},
		{"renamed bundle", `"/Users/test/Applications/Browser \"Test\".app"`, `/Users/test/Applications/Browser "Test".app`},
		{"unicode", `"/Applications/Nightly 日本語.app"`, "/Applications/Nightly 日本語.app"},
		{"empty", `""`, ""},
		{"null", `null`, ""},
		{"relative", `"Firefox.app"`, ""},
		{"executable", `"/Applications/Firefox.app/Contents/MacOS/firefox"`, ""},
		{"old lsappinfo format", `"LSDisplayName"="Firefox Nightly"`, ""},
		{"recent lsappinfo format", `"Firefox Nightly" ASN:0x0-0x76076:`, ""},
	} {
		t.Run(tt.name, func(t *testing.T) {
			got, err := parseBrowserPath([]byte(tt.data))
			if tt.want == "" {
				if err == nil || got != "" {
					t.Fatalf("expected identification failure, got %q, %v", got, err)
				}
				return
			}
			if err != nil || got != tt.want {
				t.Fatalf("got %q, %v; want %q", got, err, tt.want)
			}
		})
	}
}

func TestGetBrowserPathMissingProcess(t *testing.T) {
	path, err := getBrowserPath(2147483647)
	if err == nil || path != "" {
		t.Fatalf("expected identification failure without a fallback, got %q, %v", path, err)
	}
}
