(ns migratus-run
  (:require [clojure.edn :as edn]
            [clojure.java.io :as io]
            [clojure.string :as str]
            [migratus.core :as migratus]))

(defn- config [] (edn/read-string (slurp "migratus.edn")))

(defn- env-file-value
  [name]
  (let [env-file (io/file ".env")]
    (when (.isFile env-file)
      (with-open [reader (io/reader env-file)]
        (some (fn [line]
                (let [[key value] (str/split line #"=" 2)]
                  (when (= name (str/trim key))
                    (some-> value
                            str/trim
                            not-empty))))
              (line-seq reader))))))

(defn- database-url
  []
  (let [environment (System/getenv)]
    (if (.containsKey environment "DATABASE_URL")
      (.get environment "DATABASE_URL")
      (env-file-value "DATABASE_URL"))))

(defn- database-config
  []
  (let [database-url (database-url)]
    (when-not (seq database-url)
      (throw (ex-info "DATABASE_URL is required to apply migrations." {})))
    (assoc (config) :db {:connection-uri database-url})))

(defn -main
  [command & args]
  (case command
    "migrate" (migratus/migrate (database-config))
    "create" (migratus/create (config) (first args))
    (throw (ex-info "Expected migrate or create command."
                    {:command command, :args args}))))
