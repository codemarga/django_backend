from coderun.models import Problem, TestCase, Category

# Create categories
categories = {
    "Array": Category.objects.create(name="Array"),
    "String": Category.objects.create(name="String"),
    "Hash Table": Category.objects.create(name="Hash Table"),
    "Dynamic Programming": Category.objects.create(name="Dynamic Programming"),
    "Math": Category.objects.create(name="Math"),
    "Sorting": Category.objects.create(name="Sorting"),
    "Greedy": Category.objects.create(name="Greedy"),
    "Algorithms": Category.objects.create(name="Algorithms"),
    "Database": Category.objects.create(name="Database"),
    "Shell": Category.objects.create(name="Shell"),
    "Concurrency": Category.objects.create(name="Concurrency"),
    "JavaScript": Category.objects.create(name="JavaScript"),
}

# Helper function to create problems and test cases
def create_problem(title, description, examples, class_name, method_name, default_code, constraints, followup, categories_list, test_cases):
    problem = Problem.objects.create(
        title=title,
        description=description,
        examples=examples,
        class_name=class_name,
        method_name=method_name,
        default_code=default_code,
        constraints=constraints,
        followup=followup,
    )
    for category in categories_list:
        problem.categories.add(categories[category])
    for test_case in test_cases:
        TestCase.objects.create(
            problem=problem,
            input_data=test_case["input_data"],
            expected_output=test_case["expected_output"],
        )

# Problem definitions
problems_data = [
    {
        "title": "Two Sum",
        "description": (
            "Given an array of integers nums and an integer target, "
            "return indices of the two numbers such that they add up to target.\n\n"
            "You may assume that each input would have exactly one solution, "
            "and you may not use the same element twice.\n\n"
            "You can return the answer in any order."
        ),
        "examples": [
            {
                "input": "nums = [2,7,11,15], target = 9",
                "output": "[0,1]",
                "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1].",
            }
        ],
        "class_name": "Solution",
        "method_name": "twoSum",
        "default_code": {
            "python": "class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:",
        },
        "constraints": "2 <= nums.length <= 10^4\n-10^9 <= nums[i] <= 10^9\n-10^9 <= target <= 10^9.",
        "followup": "Can you come up with an algorithm that is less than O(n^2) time complexity?",
        "categories_list": ["Array", "Hash Table"],
        "test_cases": [
            {"input_data": {"nums": [2, 7, 11, 15], "target": 9}, "expected_output": [0, 1]},
            {"input_data": {"nums": [3, 2, 4], "target": 6}, "expected_output": [1, 2]},
            {"input_data": {"nums": [3, 3], "target": 6}, "expected_output": [0, 1]},
        ],
    },
    {
        "title": "Palindrome Check",
        "description": "Determine if a given string is a palindrome.",
        "examples": [
            {"input": "s = 'racecar'", "output": "True"},
            {"input": "s = 'hello'", "output": "False"},
        ],
        "class_name": "Solution",
        "method_name": "isPalindrome",
        "default_code": {
            "python": "class Solution:\n    def isPalindrome(self, s: str) -> bool:",
        },
        "constraints": "1 <= len(s) <= 10^5\ns consists of only printable ASCII characters.",
        "followup": "Can you solve it using O(1) additional space?",
        "categories_list": ["String", "Algorithms"],
        "test_cases": [
            {"input_data": {"s": "racecar"}, "expected_output": True},
            {"input_data": {"s": "hello"}, "expected_output": False},
            {"input_data": {"s": "A man, a plan, a canal: Panama"}, "expected_output": True},
        ],
    },
    {
        "title": "Maximum Subarray",
        "description": "Find the contiguous subarray with the largest sum.",
        "examples": [
            {"input": "nums = [-2,1,-3,4,-1,2,1,-5,4]", "output": "6"},
        ],
        "class_name": "Solution",
        "method_name": "maxSubArray",
        "default_code": {
            "python": "class Solution:\n    def maxSubArray(self, nums: List[int]) -> int:",
        },
        "constraints": "1 <= nums.length <= 10^5\n-10^4 <= nums[i] <= 10^4.",
        "followup": "Can you implement this using O(n) time complexity?",
        "categories_list": ["Array", "Dynamic Programming"],
        "test_cases": [
            {"input_data": {"nums": [-2, 1, -3, 4, -1, 2, 1, -5, 4]}, "expected_output": 6},
            {"input_data": {"nums": [1]}, "expected_output": 1},
            {"input_data": {"nums": [5, 4, -1, 7, 8]}, "expected_output": 23},
        ],
    },
    {
        "title": "Reverse Integer",
        "description": "Given a signed 32-bit integer x, reverse its digits.",
        "examples": [
            {"input": "x = 123", "output": "321"},
        ],
        "class_name": "Solution",
        "method_name": "reverse",
        "default_code": {
            "python": "class Solution:\n    def reverse(self, x: int) -> int:",
        },
        "constraints": "-2^31 <= x <= 2^31 - 1.",
        "followup": "How would you handle overflow?",
        "categories_list": ["Math", "String"],
        "test_cases": [
            {"input_data": {"x": 123}, "expected_output": 321},
            {"input_data": {"x": -123}, "expected_output": -321},
            {"input_data": {"x": 120}, "expected_output": 21},
        ],
    },
    # Add 6 more problems with similar format...
]

# Create problems
for problem_data in problems_data:
    create_problem(**problem_data)
