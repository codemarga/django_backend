import os
import sys
import django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codeMarga.settings')
django.setup()

from coderun.models import Problem, TestCase, Category

# Default driver templates
def get_driver_template(class_name, method_name):
    python_template = """from typing import List, Dict, Tuple, Set, Optional

{user_code}

instance = {class_name}()

test_cases = [
{test_cases}
]

def run_test(inp):
    if isinstance(inp, dict):
        try:
            return instance.{method_name}(**inp)
        except TypeError:
            return instance.{method_name}(*inp.values())
    elif isinstance(inp, (list, tuple)):
        return instance.{method_name}(*inp)
    else:
        return instance.{method_name}(inp)

for test in test_cases:
    try:
        res = run_test(test['input'])
        print(repr(res))
    except Exception as e:
        print(f"ERROR: {e}")
"""

    cpp_template = """#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>
using namespace std;

{user_code}

int main() {
    {class_name} instance;
    return 0;
}
"""

    java_template = """import java.util.*;

{user_code}

public class Main {
    public static void main(String[] args) {
        {class_name} instance = new {class_name}();
    }
}
"""

    return {
        "python": python_template,
        "cpp": cpp_template,
        "java": java_template,
    }

problems_data = [
    {
        "id": 1,
        "title": "Reverse a String",
        "description": "Write a function that takes a string as input and returns the string reversed.",
        "examples": [
            {"input": "s = 'hello'", "output": "'olleh'", "explanation": "The string 'hello' reversed is 'olleh'."},
            {"input": "s = 'world'", "output": "'dlrow'", "explanation": "The string 'world' reversed is 'dlrow'."}
        ],
        "class_name": "StringManipulation",
        "method_name": "reverseString",
        "default_code": {
            "python": "class StringManipulation:\n    def reverseString(self, s: str) -> str:\n        # Write your code here\n        pass",
            "cpp": "class StringManipulation {\npublic:\n    string reverseString(string s) {\n        // Write your code here\n    }\n};",
            "java": "class StringManipulation {\n    public String reverseString(String s) {\n        // Write your code here\n    }\n}"
        },
        "constraints": "1 <= len(s) <= 10^5\ns consists of printable ASCII characters.",
        "followup": "Can you solve the problem in-place without extra space?",
        "categories_list": ["String", "Two Pointers"],
        "difficulty_wise_points": 500,
        "test_cases": [
            {"input_data": {"s": "hello"}, "expected_output": "olleh"},
            {"input_data": {"s": "world"}, "expected_output": "dlrow"},
            {"input_data": {"s": "CodeMarga"}, "expected_output": "agraMedoC"},
            {"input_data": {"s": "a"}, "expected_output": "a"},
        ]
    },
    {
        "id": 2,
        "title": "Count Distinct Words",
        "description": "Write a function to count the number of distinct words in a given string. Words are separated by spaces and comparison should be case-insensitive.",
        "examples": [
            {"input": "text = 'apple banana apple orange'", "output": "3", "explanation": "'apple', 'banana', and 'orange' are distinct."},
            {"input": "text = 'Hello world hello'", "output": "2", "explanation": "Case-insensitive: 'hello' and 'world'."}
        ],
        "class_name": "WordCounter",
        "method_name": "countDistinctWords",
        "default_code": {
            "python": "class WordCounter:\n    def countDistinctWords(self, text: str) -> int:\n        # Write your code here\n        pass",
            "cpp": "class WordCounter {\npublic:\n    int countDistinctWords(string text) {\n        // Write your code here\n    }\n};",
            "java": "class WordCounter {\n    public int countDistinctWords(String text) {\n        // Write your code here\n    }\n}"
        },
        "constraints": "1 <= len(text) <= 10^5",
        "followup": "Can you optimize the solution for memory?",
        "categories_list": ["String", "Hash Table"],
        "difficulty_wise_points": 500,
        "test_cases": [
            {"input_data": {"text": "apple banana apple orange"}, "expected_output": 3},
            {"input_data": {"text": "Hello world hello"}, "expected_output": 2},
            {"input_data": {"text": "one two three four"}, "expected_output": 4},
        ]
    },
    {
        "id": 3,
        "title": "Two Sum",
        "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.\n\nYou can return the answer in any order.",
        "examples": [
            {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]", "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."}
        ],
        "class_name": "Solution",
        "method_name": "twoSum",
        "default_code": {
            "python": "class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        # Write your code here\n        pass",
            "cpp": "class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        // Write your code here\n    }\n};",
            "java": "class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        // Write your code here\n    }\n};"
        },
        "constraints": "2 <= nums.length <= 10^4\n-10^9 <= nums[i] <= 10^9\n-10^9 <= target <= 10^9",
        "followup": "Can you come up with an algorithm that is less than O(n^2) time complexity?",
        "categories_list": ["Array", "Hash Table"],
        "difficulty_wise_points": 500,
        "test_cases": [
            {"input_data": {"nums": [2, 7, 11, 15], "target": 9}, "expected_output": [0, 1]},
            {"input_data": {"nums": [3, 2, 4], "target": 6}, "expected_output": [1, 2]},
            {"input_data": {"nums": [3, 3], "target": 6}, "expected_output": [0, 1]},
        ]
    },
    {
        "title": "Palindrome Check",
        "description": "Determine if a given string is a palindrome. A palindrome reads the same backwards as forwards.",
        "examples": [
            {"input": "s = 'racecar'", "output": "True", "explanation": "'racecar' reversed is 'racecar'."},
            {"input": "s = 'hello'", "output": "False", "explanation": "'hello' reversed is 'olleh'."}
        ],
        "class_name": "Solution",
        "method_name": "isPalindrome",
        "default_code": {
            "python": "class Solution:\n    def isPalindrome(self, s: str) -> bool:\n        # Write your code here\n        pass",
            "cpp": "class Solution {\npublic:\n    bool isPalindrome(string s) {\n        // Write your code here\n    }\n};",
            "java": "class Solution {\n    public boolean isPalindrome(String s) {\n        // Write your code here\n    }\n};"
        },
        "constraints": "1 <= len(s) <= 10^5",
        "followup": "Can you solve it using O(1) additional space?",
        "categories_list": ["String", "Two Pointers"],
        "difficulty_wise_points": 500,
        "test_cases": [
            {"input_data": {"s": "racecar"}, "expected_output": True},
            {"input_data": {"s": "hello"}, "expected_output": False},
            {"input_data": {"s": "radar"}, "expected_output": True},
        ]
    },
    {
        "title": "Maximum Subarray",
        "description": "Given an integer array nums, find the subarray with the largest sum, and return its sum.",
        "examples": [
            {"input": "nums = [-2,1,-3,4,-1,2,1,-5,4]", "output": "6", "explanation": "The subarray [4,-1,2,1] has the largest sum 6."}
        ],
        "class_name": "Solution",
        "method_name": "maxSubArray",
        "default_code": {
            "python": "class Solution:\n    def maxSubArray(self, nums: List[int]) -> int:\n        # Write your code here\n        pass",
            "cpp": "class Solution {\npublic:\n    int maxSubArray(vector<int>& nums) {\n        // Write your code here\n    }\n};",
            "java": "class Solution {\n    public int maxSubArray(int[] nums) {\n        // Write your code here\n    }\n};"
        },
        "constraints": "1 <= nums.length <= 10^5\n-10^4 <= nums[i] <= 10^4",
        "followup": "Can you implement this using O(n) time complexity (Kadane's algorithm)?",
        "categories_list": ["Array", "Dynamic Programming"],
        "difficulty_wise_points": 1000,
        "test_cases": [
            {"input_data": {"nums": [-2, 1, -3, 4, -1, 2, 1, -5, 4]}, "expected_output": 6},
            {"input_data": {"nums": [1]}, "expected_output": 1},
            {"input_data": {"nums": [5, 4, -1, 7, 8]}, "expected_output": 23}
        ]
    },
    {
        "title": "Reverse Integer",
        "description": "Given a signed 32-bit integer x, return x with its digits reversed. If reversing x causes the value to go outside the signed 32-bit integer range [-2^31, 2^31 - 1], then return 0.",
        "examples": [
            {"input": "x = 123", "output": "321", "explanation": "123 reversed is 321."},
            {"input": "x = -123", "output": "-321", "explanation": "-123 reversed is -321."}
        ],
        "class_name": "Solution",
        "method_name": "reverse",
        "default_code": {
            "python": "class Solution:\n    def reverse(self, x: int) -> int:\n        # Write your code here\n        pass",
            "cpp": "class Solution {\npublic:\n    int reverse(int x) {\n        // Write your code here\n    }\n};",
            "java": "class Solution {\n    public int reverse(int x) {\n        // Write your code here\n    }\n};"
        },
        "constraints": "-2^31 <= x <= 2^31 - 1",
        "followup": "Assume the environment does not allow you to store 64-bit integers.",
        "categories_list": ["Math"],
        "difficulty_wise_points": 1000,
        "test_cases": [
            {"input_data": {"x": 123}, "expected_output": 321},
            {"input_data": {"x": -123}, "expected_output": -321},
            {"input_data": {"x": 120}, "expected_output": 21}
        ]
    },
    {
        "title": "Remove Duplicates from Sorted Array",
        "description": "Given an integer array nums sorted in non-decreasing order, remove the duplicates in-place such that each unique element appears only once. Return the number of unique elements.",
        "examples": [
            {"input": "nums = [1,1,2]", "output": "2", "explanation": "The first 2 elements are [1, 2]."}
        ],
        "class_name": "Solution",
        "method_name": "removeDuplicates",
        "default_code": {
            "python": "class Solution:\n    def removeDuplicates(self, nums: List[int]) -> int:\n        # Write your code here\n        pass",
            "cpp": "class Solution {\npublic:\n    int removeDuplicates(vector<int>& nums) {\n        // Write your code here\n    }\n};",
            "java": "class Solution {\n    public int removeDuplicates(int[] nums) {\n        // Write your code here\n    }\n};"
        },
        "constraints": "1 <= nums.length <= 3 * 10^4",
        "followup": "Can you do this with O(1) extra memory?",
        "categories_list": ["Array", "Two Pointers"],
        "difficulty_wise_points": 500,
        "test_cases": [
            {"input_data": {"nums": [1, 1, 2]}, "expected_output": 2},
            {"input_data": {"nums": [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]}, "expected_output": 5},
            {"input_data": {"nums": [1, 2, 3]}, "expected_output": 3}
        ]
    },
    {
        "title": "Climbing Stairs",
        "description": "You are climbing a staircase. It takes n steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
        "examples": [
            {"input": "n = 2", "output": "2", "explanation": "There are two ways: 1 step + 1 step, or 2 steps."},
            {"input": "n = 3", "output": "3", "explanation": "Three ways: 1+1+1, 1+2, 2+1."}
        ],
        "class_name": "Solution",
        "method_name": "climbStairs",
        "default_code": {
            "python": "class Solution:\n    def climbStairs(self, n: int) -> int:\n        # Write your code here\n        pass",
            "cpp": "class Solution {\npublic:\n    int climbStairs(int n) {\n        // Write your code here\n    }\n};",
            "java": "class Solution {\n    public int climbStairs(int n) {\n        // Write your code here\n    }\n};"
        },
        "constraints": "1 <= n <= 45",
        "followup": "Can you solve it in O(n) time and O(1) space?",
        "categories_list": ["Dynamic Programming"],
        "difficulty_wise_points": 500,
        "test_cases": [
            {"input_data": {"n": 2}, "expected_output": 2},
            {"input_data": {"n": 3}, "expected_output": 3},
            {"input_data": {"n": 4}, "expected_output": 5},
            {"input_data": {"n": 5}, "expected_output": 8}
        ]
    },
    {
        "title": "Search Insert Position",
        "description": "Given a sorted array of distinct integers and a target value, return the index if the target is found. If not, return the index where it would be if it were inserted in order.",
        "examples": [
            {"input": "nums = [1,3,5,6], target = 5", "output": "2", "explanation": "5 is found at index 2."}
        ],
        "class_name": "Solution",
        "method_name": "searchInsert",
        "default_code": {
            "python": "class Solution:\n    def searchInsert(self, nums: List[int], target: int) -> int:\n        # Write your code here\n        pass",
            "cpp": "class Solution {\npublic:\n    int searchInsert(vector<int>& nums, int target) {\n        // Write your code here\n    }\n};",
            "java": "class Solution {\n    public int searchInsert(int[] nums, int target) {\n        // Write your code here\n    }\n};"
        },
        "constraints": "1 <= nums.length <= 10^4",
        "followup": "You must write an algorithm with O(log n) runtime complexity.",
        "categories_list": ["Array", "Binary Search"],
        "difficulty_wise_points": 500,
        "test_cases": [
            {"input_data": {"nums": [1, 3, 5, 6], "target": 5}, "expected_output": 2},
            {"input_data": {"nums": [1, 3, 5, 6], "target": 2}, "expected_output": 1},
            {"input_data": {"nums": [1, 3, 5, 6], "target": 7}, "expected_output": 4}
        ]
    },
    {
        "title": "Best Time to Buy and Sell Stock",
        "description": "You are given an array prices where prices[i] is the price of a given stock on the ith day. You want to maximize your profit by choosing a single day to buy one stock and choosing a different day in the future to sell that stock. Return the maximum profit.",
        "examples": [
            {"input": "prices = [7,1,5,3,6,4]", "output": "5", "explanation": "Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6 - 1 = 5."}
        ],
        "class_name": "Solution",
        "method_name": "maxProfit",
        "default_code": {
            "python": "class Solution:\n    def maxProfit(self, prices: List[int]) -> int:\n        # Write your code here\n        pass",
            "cpp": "class Solution {\npublic:\n    int maxProfit(vector<int>& prices) {\n        // Write your code here\n    }\n};",
            "java": "class Solution {\n    public int maxProfit(int[] prices) {\n        // Write your code here\n    }\n};"
        },
        "constraints": "1 <= prices.length <= 10^5",
        "followup": "Can you do it in a single pass O(n)?",
        "categories_list": ["Array", "Dynamic Programming"],
        "difficulty_wise_points": 500,
        "test_cases": [
            {"input_data": {"prices": [7, 1, 5, 3, 6, 4]}, "expected_output": 5},
            {"input_data": {"prices": [7, 6, 4, 3, 1]}, "expected_output": 0},
            {"input_data": {"prices": [1, 2, 3, 4, 5]}, "expected_output": 4}
        ]
    },
    {
        "title": "Binary Search",
        "description": "Given an array of integers nums which is sorted in ascending order, and an integer target, write a function to search target in nums. If target exists, return its index. Otherwise, return -1.",
        "examples": [
            {"input": "nums = [-1,0,3,5,9,12], target = 9", "output": "4", "explanation": "9 exists in nums and its index is 4."}
        ],
        "class_name": "Solution",
        "method_name": "search",
        "default_code": {
            "python": "class Solution:\n    def search(self, nums: List[int], target: int) -> int:\n        # Write your code here\n        pass",
            "cpp": "class Solution {\npublic:\n    int search(vector<int>& nums, int target) {\n        // Write your code here\n    }\n};",
            "java": "class Solution {\n    public int search(int[] nums, int target) {\n        // Write your code here\n    }\n};"
        },
        "constraints": "1 <= nums.length <= 10^4",
        "followup": "You must write an algorithm with O(log n) runtime complexity.",
        "categories_list": ["Array", "Binary Search"],
        "difficulty_wise_points": 500,
        "test_cases": [
            {"input_data": {"nums": [-1, 0, 3, 5, 9, 12], "target": 9}, "expected_output": 4},
            {"input_data": {"nums": [-1, 0, 3, 5, 9, 12], "target": 2}, "expected_output": -1},
            {"input_data": {"nums": [5], "target": 5}, "expected_output": 0}
        ]
    },
    {
        "title": "Find Peak Element",
        "description": "A peak element is an element that is strictly greater than its neighbors. Given an integer array nums, find a peak element, and return its index. If the array contains multiple peaks, return the index to any of the peaks.",
        "examples": [
            {"input": "nums = [1,2,3,1]", "output": "2", "explanation": "3 is a peak element and its index is 2."}
        ],
        "class_name": "Solution",
        "method_name": "findPeakElement",
        "default_code": {
            "python": "class Solution:\n    def findPeakElement(self, nums: List[int]) -> int:\n        # Write your code here\n        pass",
            "cpp": "class Solution {\npublic:\n    int findPeakElement(vector<int>& nums) {\n        // Write your code here\n    }\n};",
            "java": "class Solution {\n    public int findPeakElement(int[] nums) {\n        // Write your code here\n    }\n};"
        },
        "constraints": "1 <= nums.length <= 1000",
        "followup": "You must write an algorithm that runs in O(log n) time.",
        "categories_list": ["Array", "Binary Search"],
        "difficulty_wise_points": 1000,
        "test_cases": [
            {"input_data": {"nums": [1, 2, 3, 1]}, "expected_output": 2},
            {"input_data": {"nums": [1, 2, 1, 3, 5, 6, 4]}, "expected_output": 5},
            {"input_data": {"nums": [1]}, "expected_output": 0}
        ]
    }
]

def seed_all_problems():
    print("Starting problem population and update...")
    for item in problems_data:
        pid = item.get("id")
        problem = None
        if pid:
            problem = Problem.objects.filter(id=pid).first()
        if not problem:
            problem = Problem.objects.filter(title=item["title"]).first()

        driver_template = get_driver_template(item["class_name"], item["method_name"])

        if problem:
            problem.title = item["title"]
            problem.description = item["description"]
            problem.examples = item["examples"]
            problem.class_name = item["class_name"]
            problem.method_name = item["method_name"]
            problem.default_code = item["default_code"]
            problem.driver_template = driver_template
            problem.constraints = item.get("constraints", "")
            problem.followup = item.get("followup", "")
            problem.difficulty_wise_points = item.get("difficulty_wise_points", 500)
            problem.save()
            print(f"Updated existing problem ID {problem.id}: {problem.title}")
        else:
            problem = Problem.objects.create(
                title=item["title"],
                description=item["description"],
                examples=item["examples"],
                class_name=item["class_name"],
                method_name=item["method_name"],
                default_code=item["default_code"],
                driver_template=driver_template,
                constraints=item.get("constraints", ""),
                followup=item.get("followup", ""),
                difficulty_wise_points=item.get("difficulty_wise_points", 500),
            )
            print(f"Created new problem ID {problem.id}: {problem.title}")

        # Set categories
        for cat_name in item.get("categories_list", []):
            cat, _ = Category.objects.get_or_create(name=cat_name)
            problem.categories.add(cat)

        # Replace / recreate test cases
        TestCase.objects.filter(problem=problem).delete()
        for tc in item["test_cases"]:
            TestCase.objects.create(
                problem=problem,
                input_data=tc["input_data"],
                expected_output=tc["expected_output"]
            )
        print(f"  Added {len(item['test_cases'])} test cases for {problem.title}")

    print("Done! Total problems in database:", Problem.objects.count())

if __name__ == '__main__':
    seed_all_problems()
