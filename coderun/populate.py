from coderun.models import Problem, TestCase

# Create the problem
two_sum_problem = Problem.objects.create(
    title="Two Sum",
    description=(
        "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\n\n"
        "You may assume that each input would have exactly one solution, and you may not use the same element twice.\n\n"
        "You can return the answer in any order."
    ),
    examples=[
        {
            "input": "nums = [2,7,11,15], target = 9",
            "output": "[0,1]",
            "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1].",
        },
        {
            "input": "nums = [3,2,4], target = 6",
            "output": "[1,2]",
            "explanation": "Because nums[1] + nums[2] == 6, we return [1, 2].",
        },
        {
            "input": "nums = [3,3], target = 6",
            "output": "[0,1]",
            "explanation": "Because nums[0] + nums[1] == 6, we return [0, 1].",
        },
    ],
    class_name="Solution",
    method_name="twoSum",
    default_code={
        "python": "class Solution(object):\n    def twoSum(self, nums, target):",
        "cpp": "class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n    }\n};",
        "java": "class Solution {\n    public int[] twoSum(int[] nums, int target) {\n    }\n};",
    },
    constraints=(
        "2 <= nums.length <= 10^4\n"
        "-10^9 <= nums[i] <= 10^9\n"
        "-10^9 <= target <= 10^9\n"
        "Only one valid answer exists."
    ),
    followup="Can you come up with an algorithm that is less than O(n^2) time complexity?",
)

# Create test cases
TestCase.objects.create(
    problem=two_sum_problem,
    input_data={"nums": [2, 7, 11, 15], "target": 9},
    expected_output=[0, 1],
)

TestCase.objects.create(
    problem=two_sum_problem,
    input_data={"nums": [3, 2, 4], "target": 6},
    expected_output=[1, 2],
)

TestCase.objects.create(
    problem=two_sum_problem,
    input_data={"nums": [3, 3], "target": 6},
    expected_output=[0, 1],
)
