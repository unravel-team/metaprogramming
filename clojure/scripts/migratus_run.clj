(ns migratus-run
  (:require [clojure.edn :as edn]
            [migratus.core :as migratus]))

(defn- config [] (edn/read-string (slurp "migratus.edn")))

(defn- database-config
  []
  (let [database-url (System/getenv "DATABASE_URL")]
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
