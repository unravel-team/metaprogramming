(ns sync-deps-org
  (:require [clojure.java.io :as io]))

(def ^:private source-block "#+begin_src clojure :tangle \"deps.edn\"")

(defn- synchronize
  [org dependencies]
  (let [block-start (.indexOf org source-block)
        content-start (+ block-start (count source-block))
        block-end (.indexOf org "#+end_src" content-start)]
    (when (or (neg? block-start) (neg? block-end))
      (throw (ex-info "Could not find the deps.edn Org source block." {})))
    (str (subs org 0 (inc content-start)) dependencies (subs org block-end))))

(defn -main
  []
  (let [org-file (io/file "clojure.org")
        deps-file (io/file "deps.edn")]
    (spit org-file (synchronize (slurp org-file) (slurp deps-file)))))
