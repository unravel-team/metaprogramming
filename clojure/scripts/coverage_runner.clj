(ns coverage-runner
  (:require [clofidence.main :as clofidence]
            [clofidence.report-renderer :as renderer]
            [cognitect.test-runner.api :as test-runner]))

(def ^:dynamic *test-failure* nil)

(defn run-tests
  [opts]
  (try (test-runner/test opts)
       (catch Throwable error (reset! *test-failure* error))))

(defn- report-and-save
  [coords-cov forms opts]
  (let [total-hits (#'clofidence/total-coords-hits coords-cov)]
    (if (zero? total-hits)
      (println
        "\n\n Nothing recorded, so no report will be generated. Did you setup clojure.storm.instrumentOnlyPrefixes correctly?")
      (do (println
            (format
              "Captured a total of %d forms coordinates hits for %d forms."
              total-hits
              (count coords-cov)))
          (println "Building and saving report...")
          (let [report (#'clofidence/make-report forms coords-cov)
                report-index-html (renderer/render-index-html report opts)
                namespace-reports (renderer/render-namespaces-details-reports
                                    report)]
            (#'clofidence/save report-index-html namespace-reports opts))
          (println "All done")))))

(defn run
  [opts]
  (let [test-failure (atom nil)]
    (binding [*test-failure* test-failure]
      (with-redefs [clofidence/report-and-save report-and-save]
        (clofidence/run (assoc opts :test-fn `run-tests))))
    (when-let [error @test-failure] (throw error))))
