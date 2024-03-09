module Main where

import Control.Monad
import Data.Monoid
import Data.List
import Data.Bool
import Text.Printf

(.:) = (.) . (.)

lockers :: Int
lockers = 230

digits :: Int -> [Int]
digits = map (`mod` 10) . reverse . takeWhile (> 0) . iterate (`div` 10)

foolproofDivisibilityTests, allDivisibilityTests :: [Int]
foolproofDivisibilityTests = [2,3,5]
allDivisibilityTests = foolproofDivisibilityTests ++ [11]

isSquare :: Int -> Bool
isSquare x = let s = floor $ sqrt $ fromIntegral x in s * s == x && s <= 13

divisibilityTestBy :: Int -> Int -> Bool
divisibilityTestBy 2 2    = True
divisibilityTestBy 3 3    = True
divisibilityTestBy 5 5    = True
divisibilityTestBy 7 7    = True

divisibilityTestBy x 2  = (x `mod` 10) `elem` [0, 2, 4, 6, 8]
divisibilityTestBy x 3  = if x `div` 10 == 0 then x `elem` [3, 6, 9] else sum (digits x) `divisibilityTestBy` 3
divisibilityTestBy x 5  = (x `mod` 10) `elem` [0, 5]
-- NOTE: Not foolproof divisibility tests
divisibilityTestBy x 11 = let d = digits x in length d == 2 && head d == d !! 1
divisibilityTestBy _ _ = False

test :: Int -> IO ()
test n = go 1
  where
    go i =
      let expected = i `mod` n == 0; actual = i `divisibilityTestBy` n in
      if expected /= actual
      then putStrLn $
        "Failed at " ++ show i ++ " for divisibility by " ++ show n ++
        ". Expected = " ++ show expected ++ ", actual = " ++ show actual
      else when (i <= lockers) $ go $ succ i

primes :: [Int]
primes = sieve [2..]
  where
    sieve (p:xs) = p : sieve [x | x <- xs, x `mod` p /= 0]

isPrimeLooking :: Int -> Bool
isPrimeLooking n = n `elem` [2, 3, 5, 7, 11, 13, 17, 19] || (not (passesDivisibilityTests n) && not (isSquare n))
  where
    passesDivisibilityTests = getAny . foldMap (Any .: flip divisibilityTestBy) allDivisibilityTests


leftSortedDiff :: Ord a => [a] -> [a] -> [a]
leftSortedDiff (x:xs) (y:ys) = case x `compare` y of
  LT -> x : leftSortedDiff xs (y:ys)
  EQ -> leftSortedDiff xs ys
  GT -> leftSortedDiff (x:xs) ys
leftSortedDiff [] ys = ys
leftSortedDiff xs [] = xs

realPrimes = takeWhile (<= lockers) $ primes
lookingPrime = filter isPrimeLooking [1..lockers]

powersOfTwo = takeWhile (<= lockers) $ concatMap (\x -> [x-1, x]) $ iterate (2*) 2
fibs = 0 : 1 : zipWith (+) fibs (tail fibs)

main :: IO ()
main = do
  forM_ foolproofDivisibilityTests test
  putStrLn $ "Left out primes: " ++ (show $ leftSortedDiff realPrimes lookingPrime)
  putStrLn $ "Fake primes: " ++ (show $ leftSortedDiff lookingPrime realPrimes)
  putStrLn $ "Available lockers using 2-powers: " ++ show (length powersOfTwo)
  putStrLn $ "Available lockers using fibs: " ++ show (length $ takeWhile (<= lockers) fibs)
  putStrLn $ "Available lockers using looking like primes: " ++ show (length lookingPrime)
  putStrLn $ "Available lockers using primes: " ++ show (length realPrimes)


  forM_ (leftSortedDiff lookingPrime realPrimes) $ \n ->
      putStrLn (show n ++ " " ++ (show $ filter (\x -> n `mod` x == 0) realPrimes))

count = sum . map (bool 0 1)

-- https://en.wikipedia.org/wiki/Precision_and_recall#Definition
confusion t p = length $ filter (\n -> elem n realPrimes == t && elem n lookingPrime == p) [1..lockers]

tp, fp, tn, fn :: Float
tp = fromIntegral $ confusion True  True
fp = fromIntegral $ confusion False True
tn = fromIntegral $ confusion False False
fn = fromIntegral $ confusion True  False

accuraccy, precision, recall, f1 :: String
accuraccy = printf "%.2f" $ (tp + tn) / 230
precision = printf "%.2f" $ tp / fromIntegral (length lookingPrime)
recall    = printf "%.2f" $ tp / fromIntegral (length realPrimes)
f1        = printf "%.2f" $ 2 * tp / (2 * (tp + fp + fn))


table = "<tr>" ++ (concat $ intersperse "\n</tr><tr>\n" $ map (\n -> "<td>" ++ show n ++ "</td>" ++ (toHtml $ primeDivisors n)) fakes) ++ "</tr>"
  where
    fakes = leftSortedDiff lookingPrime realPrimes
    primeDivisors n = filter (\x -> n `mod` x == 0) realPrimes
    toMask divisors = map (\prime -> prime `elem` divisors) [7,11,13,17,19,23,29,31]
    toHtml divisors = concat $ map (bool "<td class=\"false\">F</td>" "<td class=\"true\">T</td>") $ toMask divisors
