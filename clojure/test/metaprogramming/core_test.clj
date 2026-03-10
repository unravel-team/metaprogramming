(ns metaprogramming.core-test
  (:require [clojure.test :refer [deftest is testing]]
            [metaprogramming.core :as core]))

(deftest example-test (testing "basic assertion" (is (= 1 1))))
