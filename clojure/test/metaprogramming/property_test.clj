(ns metaprogramming.property-test
  (:require [clojure.test.check.clojure-test :refer [defspec]]
            [clojure.test.check.generators :as gen]
            [clojure.test.check.properties :as prop]
            [metaprogramming.core :as core]))

(defspec ^:property doubling-is-addition
  100
  (prop/for-all [value gen/small-integer]
    (= (+ value value) (core/example value))))
