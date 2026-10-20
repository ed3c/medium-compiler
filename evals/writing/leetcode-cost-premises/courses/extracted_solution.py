from collections import deque


class Solution:
    def canFinish(self, numCourses: int, prerequisites: list[list[int]]) -> bool:
        after = [[] for _ in range(numCourses)]
        remaining = [0] * numCourses

        for course, prerequisite in prerequisites:
            after[prerequisite].append(course)
            remaining[course] += 1

        ready = deque()
        for course in range(numCourses):
            if remaining[course] == 0:
                ready.append(course)

        finished = 0
        while ready:
            course = ready.popleft()
            finished += 1
            for dependent in after[course]:
                remaining[dependent] -= 1
                if remaining[dependent] == 0:
                    ready.append(dependent)

        return finished == numCourses
