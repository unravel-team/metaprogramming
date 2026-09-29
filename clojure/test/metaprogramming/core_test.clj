(ns metaprogramming.core-test
  (:require [clojure.test :refer [deftest is testing]]
            [metaprogramming.core :as core]))

(deftest ^:unit example-test
  (testing "doubling"
    (doseq [value [0 2 -3]] (is (= (+ value value) (core/example value))))))
