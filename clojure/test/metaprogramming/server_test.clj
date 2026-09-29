(ns metaprogramming.server-test
  (:require [clojure.test :refer [deftest is testing]]
            [metaprogramming.server :as server])
  (:import [com.sun.net.httpserver HttpServer]
           [java.net URI]
           [java.net.http HttpClient HttpRequest HttpResponse$BodyHandlers]))

(deftest ^:unit health-test
  (let [^HttpServer service (server/start! 0)
        port (.getPort (.getAddress service))]
    (try (with-open [client (HttpClient/newHttpClient)]
           (doseq [[path status body] [["/health" 200 "{\"status\":\"ok\"}"]
                                       ["/missing" 404
                                        "{\"error\":\"not found\"}"]]]
             (testing path
               (let [request (-> (HttpRequest/newBuilder
                                   (URI/create
                                     (str "http://localhost:" port path)))
                                 (.GET)
                                 (.build))
                     response (.send client
                                     request
                                     (HttpResponse$BodyHandlers/ofString))]
                 (is (= status (.statusCode response)))
                 (is (= body (.body response)))))))
         (finally (.stop service 0)))))
