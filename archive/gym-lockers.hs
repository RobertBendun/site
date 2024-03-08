module Main where

import Control.Monad
import Data.Monoid

(.:) = (.) . (.)

lockers :: Int
lockers = 230

digits :: Int -> [Int]
digits = map (`mod` 10) . reverse . takeWhile (> 0) . iterate (`div` 10)

foolproofDivisibilityTests, allDivisibilityTests :: [Int]
foolproofDivisibilityTests = [2,3,5,10]
allDivisibilityTests = foolproofDivisibilityTests ++ [11]

isSquare :: Int -> Bool
isSquare x = let s = floor $ sqrt $ fromIntegral x in s * s == x && s <= 11

divisibilityTestBy :: Int -> Int -> Bool
divisibilityTestBy 2 2    = True
divisibilityTestBy 3 3    = True
divisibilityTestBy 5 5    = True
divisibilityTestBy 7 7    = True

divisibilityTestBy x 2  = (x `mod` 10) `elem` [0, 2, 4, 6, 8]
divisibilityTestBy x 3  = if x `div` 10 == 0 then x `elem` [3, 6, 9] else sum (digits x) `divisibilityTestBy` 3
divisibilityTestBy x 5  = (x `mod` 10) `elem` [0, 5]
divisibilityTestBy x 10 = (x `mod` 10) == 0
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
isPrimeLooking n = not (passesDivisibilityTests n) && not (isSquare n)
  where
    passesDivisibilityTests = getAny . foldMap (Any .: flip divisibilityTestBy) allDivisibilityTests


sortedDiff :: Ord a => [a] -> [a] -> [a]
sortedDiff (x:xs) (y:ys) = case x `compare` y of
  LT -> x : sortedDiff xs (y:ys)
  EQ -> sortedDiff xs ys
  GT -> y : sortedDiff (x:xs) ys
sortedDiff [] ys = ys
sortedDiff xs [] = xs

realPrimes = takeWhile (<= lockers) $ dropWhile (<= 20) primes
lookingPrime = filter isPrimeLooking [20..lockers]

powersOfTwo = takeWhile (<= lockers) $ concatMap (\x -> [x-1, x]) $ iterate (2*) 2
fibs = 0 : 1 : zipWith (+) fibs (tail fibs)

main :: IO ()
main = do
  forM_ foolproofDivisibilityTests test
  print $ sortedDiff realPrimes lookingPrime
  putStrLn $ "Available lockers using 2-powers: " ++ show (length powersOfTwo)
  putStrLn $ "Available lockers using fibs: " ++ show (length $ takeWhile (<= lockers) fibs)
  putStrLn $ "Available lockers using looking like primes: " ++ show (length lookingPrime)
