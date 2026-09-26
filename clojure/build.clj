(ns build
  (:refer-clojure :exclude [test])
  (:require [clojure.string :as str]
            [clojure.tools.build.api :as b]))

(def lib 'unravel.metaprogramming/clojure-scaffold)
(def class-dir "target/classes")
(def basis (delay (b/create-basis {:project "deps.edn"})))

(defn- read-version
  []
  (let [value (str/trim (slurp "VERSION"))]
    (when-not (re-matches #"\d+\.\d+\.\d+" value)
      (throw (ex-info "VERSION must contain plain semantic version"
                      {:value value})))
    value))

(defn version [_] (println (read-version)))

(defn- bump-version!
  [component]
  (let [[major minor patch] (mapv bigint (str/split (read-version) #"\."))
        bumped (case component
                 :major [(inc major) 0 0]
                 :minor [major (inc minor) 0]
                 :patch [major minor (inc patch)])
        value (str/join "." bumped)]
    (spit "VERSION" (str value "\n"))
    (println value)))

(defn major [_] (bump-version! :major))

(defn minor [_] (bump-version! :minor))

(defn patch [_] (bump-version! :patch))

(defn jar-file [] (format "target/%s-%s.jar" (name lib) (read-version)))

(defn pom-file
  []
  (format "target/classes/META-INF/maven/%s/%s/pom.xml"
          (namespace lib)
          (name lib)))

(defn library-name [_] (println lib))

(defn artifact-path [_] (println (jar-file)))

(defn pom-path [_] (println (pom-file)))

(defn- run-command!
  [command-args]
  (println (str "Running: " (str/join " " command-args)))
  (let [{:keys [exit], :as result} (b/process {:command-args command-args})]
    (when-not (zero? exit)
      (throw (ex-info (str "Command failed: " (str/join " " command-args))
                      result)))))

(defn- clojure! [& args] (run-command! (into ["clojure" "-Srepro"] args)))

(defn clean [_] (b/delete {:path "target"}))

(defn test [_] (clojure! "-M:test"))

(defn test-llm [_] (clojure! "-M:test" "-i" ":llm"))

(defn test-integration [_] (clojure! "-M:test" "-i" ":integration"))

(defn jar
  [_]
  (clean nil)
  (b/copy-dir {:src-dirs ["src"], :target-dir class-dir})
  (b/write-pom {:class-dir class-dir,
                :lib lib,
                :version (read-version),
                :basis @basis,
                :src-dirs ["src"]})
  (b/jar {:class-dir class-dir, :jar-file (jar-file)})
  (println (str "Created " (jar-file))))

(defn install
  [_]
  (jar nil)
  (b/install {:basis @basis,
              :lib lib,
              :version (read-version),
              :jar-file (jar-file),
              :class-dir class-dir})
  (println (format "Installed %s %s locally" lib (read-version))))

(defn deploy [_] (run-command! ["make" "deploy-clojars"]))
