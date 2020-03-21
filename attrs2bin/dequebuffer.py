from typing import Any, Deque


class DequeBuffer(Deque[Any]):
    """
    Like `collections.deque`, but with an extra `popnleft()` method, which
    lets you indicate how many element you want to read from the left of the
    queue.
    """
    
    def popnleft(self, n: int) -> bytes:
        """
        Return `n` elements from the left of the queue.
        """
        if n > len(self):
            raise IndexError("Argument is out of range")
        return bytes(self.popleft() for _ in range(n))
