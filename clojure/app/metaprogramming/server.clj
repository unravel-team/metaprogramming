(ns metaprogramming.server
  (:import [com.sun.net.httpserver HttpExchange HttpHandler HttpServer]
           [java.net InetSocketAddress]
           [java.nio.charset StandardCharsets]))

(defn- respond!
  [^HttpExchange exchange status body]
  (let [bytes (.getBytes body StandardCharsets/UTF_8)]
    (.set (.getResponseHeaders exchange)
          "Content-Type"
          "application/json; charset=utf-8")
    (.sendResponseHeaders exchange status (alength bytes))
    (with-open [output (.getResponseBody exchange)] (.write output bytes))))

(defn- handler
  [^HttpExchange exchange]
  (if (and (= "GET" (.getRequestMethod exchange))
           (= "/health" (.getPath (.getRequestURI exchange))))
    (respond! exchange 200 "{\"status\":\"ok\"}")
    (respond! exchange 404 "{\"error\":\"not found\"}")))

(defn start!
  [port]
  (let [server (HttpServer/create (InetSocketAddress. "0.0.0.0" port) 0)]
    (.createContext server
                    "/"
                    (reify
                      HttpHandler
                        (handle [_ exchange] (handler exchange))))
    (.start server)
    server))

(defn -main
  []
  (let [port (Integer/parseInt (or (System/getenv "PORT") "8080"))]
    (start! port)
    (println (str "Clojure scaffold listening on 0.0.0.0:" port)))) ; [tag:health-route]
