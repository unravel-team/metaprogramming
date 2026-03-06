(ns metaprogramming.core-test
  (:require [clojure.test :refer [deftest is]]
            [metaprogramming.core :as core]))

(deftest add-test (is (= 5 (core/add 2 3))))
