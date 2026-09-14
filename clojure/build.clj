(ns build
  (:require [clojure.string :as str]
            [clojure.tools.build.api :as b]))

(def lib 'unravel.metaprogramming/clojure-scaffold)
(def class-dir "target/classes")
(def basis (delay (b/create-basis {:project "deps.edn"})))

(defn version
  []
  (let [value (str/trim (slurp "VERSION"))]
    (when-not (re-matches #"\d+\.\d+\.\d+" value)
      (throw (ex-info "VERSION must contain plain semantic version"
                      {:value value})))
    value))

(defn jar-file [] (format "target/%s-%s.jar" (name lib) (version)))

(defn pom-file
  []
  (format "target/classes/META-INF/maven/%s/%s/pom.xml"
          (namespace lib)
          (name lib)))

(defn library-name [_] (println lib))

(defn artifact-path [_] (println (jar-file)))

(defn pom-path [_] (println (pom-file)))

(defn clean [_] (b/delete {:path "target"}))

(defn jar
  [_]
  (clean nil)
  (b/copy-dir {:src-dirs ["src"], :target-dir class-dir})
  (b/write-pom {:class-dir class-dir,
                :lib lib,
                :version (version),
                :basis @basis,
                :src-dirs ["src"]})
  (b/jar {:class-dir class-dir, :jar-file (jar-file)})
  (println (str "Created " (jar-file))))
