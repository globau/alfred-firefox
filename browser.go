package main

import (
	"encoding/json"
	"fmt"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/deanishe/awgo/util"
)

const browserPathScript = `
ObjC.import('AppKit');
function run(args) {
    const app = $.NSRunningApplication.runningApplicationWithProcessIdentifier(Number(args[0]));
    if (app.isNil() || app.bundleURL.isNil()) {
        throw new Error('Cannot identify the connected browser');
    }
    return JSON.stringify(ObjC.unwrap(app.bundleURL.path));
}
`

func getBrowserPath(pid int) (string, error) {
	cmd := exec.Command("/usr/bin/osascript", "-l", "JavaScript", "-e", browserPathScript, strconv.Itoa(pid))
	data, err := util.RunCmd(cmd)
	if err != nil {
		return "", fmt.Errorf("cannot identify browser process %d: %w", pid, err)
	}
	return parseBrowserPath(data)
}

func parseBrowserPath(data []byte) (string, error) {
	var path string
	if err := json.Unmarshal(data, &path); err != nil {
		return "", fmt.Errorf("invalid browser application path: %w", err)
	}
	if !filepath.IsAbs(path) || !strings.EqualFold(filepath.Ext(path), ".app") {
		return "", fmt.Errorf("invalid browser application path %q", path)
	}
	return path, nil
}
