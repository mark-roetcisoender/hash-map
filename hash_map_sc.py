# Name: Mark Roetcisoender
# OSU Email: roetcism@oregonstate.edu
# Course: CS261 - Data Structures
# Assignment: Assignment 6
# Due Date: 3/14/2024
# Description: An implementation of HashMap using Separate Chaining.


from a6_include import (DynamicArray, LinkedList,
                        hash_function_1, hash_function_2)


class HashMap:
    def __init__(self,
                 capacity: int = 11,
                 function: callable = hash_function_1) -> None:
        """
        Initialize new HashMap that uses
        separate chaining for collision resolution
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        self._buckets = DynamicArray()

        # capacity must be a prime number
        self._capacity = self._next_prime(capacity)
        for _ in range(self._capacity):
            self._buckets.append(LinkedList())

        self._hash_function = function
        self._size = 0

    def __str__(self) -> str:
        """
        Override string method to provide more readable output
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        out = ''
        for i in range(self._buckets.length()):
            out += str(i) + ': ' + str(self._buckets[i]) + '\n'
        return out

    def _next_prime(self, capacity: int) -> int:
        """
        Increment from given number and the find the closest prime number
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        if capacity % 2 == 0:
            capacity += 1

        while not self._is_prime(capacity):
            capacity += 2

        return capacity

    @staticmethod
    def _is_prime(capacity: int) -> bool:
        """
        Determine if given integer is a prime number and return boolean
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        if capacity == 2 or capacity == 3:
            return True

        if capacity == 1 or capacity % 2 == 0:
            return False

        factor = 3
        while factor ** 2 <= capacity:
            if capacity % factor == 0:
                return False
            factor += 2

        return True

    def get_size(self) -> int:
        """
        Return size of map
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return self._size

    def get_capacity(self) -> int:
        """
        Return capacity of map
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return self._capacity

    # ------------------------------------------------------------------ #

    def put(self, key: str, value: object) -> None:
        """
        Takes a key and a value as parameters. If the key exists in the hash map already, update its value to be the
        parameter value. If the key doesn't exist, insert the key value pair. If the table load is >= 1 prior to
        insertion, call resize() with double the current capacity. Utilizes indirect recursion with resize().
        """
        # check if the table_load is over the threshold. If so, call resize()
        if self.table_load() >= 1:
            self.resize_table(self._capacity * 2)

        # determine where the key hashes to. If the LL at the index contains the key, update its value and return
        hashed_key = self._hash_function(key)
        index = hashed_key % self._capacity
        for node in self._buckets[index]:
            if node.key == key:
                node.value = value
                return

        # if key is not in the hash map, insert the key/value pair and increment the size
        self._buckets[index].insert(key, value)
        self._size += 1

    def resize_table(self, new_capacity: int) -> None:
        """
        Takes a parameter integer as the hash map's new capacity and resizes the capacity accordingly. If the new
        capacity is less than 1, returns without doing anything. If the parameter is not prime, updates the new
        capacity to be the next prime number. Utilizes indirect recursion with put() by calling it to insert key/value
        pairs back into the resized array.
        """
        # if the new capacity is less than 1, return
        if new_capacity < 1:
            return

        # create an array of key/value pairs to be inserted back into the table, and updates new_capacity to be
        # prime if it isn't already. Update the hash map's capacity
        key_val_array = self.get_keys_and_values()
        if self._is_prime(new_capacity) is False:
            new_capacity = self._next_prime(new_capacity)
        self._capacity = new_capacity

        # 'clear' out the hash table by assigning it to be a new DA, and appending LLs to reach the new capacity
        self._buckets = DynamicArray()
        for _ in range(self._capacity):
            self._buckets.append(LinkedList())
        self._size = 0

        # insert each key/value pair into the fresh copy of the table by calling put() on the DA of key/value pairs
        for _ in range(key_val_array.length()):
            self.put(key_val_array[_][0], key_val_array[_][1])

    def table_load(self) -> float:
        """
        Returns the current table load of the hash map
        """
        return self._size / self._capacity

    def empty_buckets(self) -> int:
        """
        Returns the amount of empty LinkedLists, or buckets in the hash map.
        """
        # iterate through the self._buckets DA, and if the LL at an index contains no nodes, increment the count
        empty_buckets = 0
        for _ in range(self._capacity):
            # print(self._buckets.length())
            if self._buckets[_].length() == 0:
                empty_buckets += 1
        return empty_buckets

    def get(self, key: str):
        """
        Returns the value paired with the parameter key. Returns None if the key does not exist in the hash map.
        Utilizes contains_key() and LinkedList()'s contains() method.
        """
        # find if the key exists, and if so, call LL()'s contains() method to access the value at that node
        if self.contains_key(key) is True:
            hashed_key = self._hash_function(key)
            index = hashed_key % self._capacity
            node = self._buckets[index].contains(key)
            return node.value
        return None

    def contains_key(self, key: str) -> bool:
        """
        Returns True if the parameter key is in the hash map, and False otherwise. Utilizes LinkedList()'s contains()
        method.
        """
        # find the index the key hashes to and use LL()'s contain() method to determine if the LL contains the key
        hashed_key = self._hash_function(key)
        index = hashed_key % self._capacity
        if self._buckets[index].contains(key) is not None:
            return True
        return False

    def remove(self, key: str) -> None:
        """
        Removes the parameter key from the hash map if it exists in the hash map. If it isn't, nothing occurs. Uses
        LinkedList()'s remove() method.
        """
        # find the index where the key hashes to, and use LL()'s remove() method to remove the key if it's there
        hashed_key = self._hash_function(key)
        index = hashed_key % self._capacity
        if self._buckets[index].remove(key) is True:
            self._size -= 1

    def get_keys_and_values(self) -> DynamicArray:
        """
        Returns a DynamicArray containing tuples of the key/values pairs from the hashmap. Iterates over each element
        in the hash map once.
        """
        # create a DA to store the tuples
        key_value_da = DynamicArray()

        # Go through the bucket, and if there is a non-None LL, add its key/value pairs to the tuple DA
        for _ in range(self._capacity):
            for node in self._buckets[_]:
                k_v_tuple = (node.key, node.value)
                key_value_da.append(k_v_tuple)
        return key_value_da

    def clear(self) -> None:
        """
        Clears the contents of the current hashmap by initializing each 'bucket' to a fresh LinkedList. Does not
        impact the capacity.
        """
        # create a new LL at each index in the bucket DA.
        for _ in range(self._capacity):
            self._buckets[_] = LinkedList()
        self._size = 0


def find_mode(da: DynamicArray) -> tuple[DynamicArray, int]:
    """
    Function outside the HashMap class which takes an unsorted DynamicArray as a parameter, and returns a tuple
    containing a dynamic array of the most occurring value(s) in the parameter, and an integer representing how many
    times they occur. There can be multiple mode values
    """
    # create a HashMap to utilize, a DA to contain the mode, and a counter
    map = HashMap()
    mode_da = DynamicArray()
    count = 0

    # traverse the parameter DA, inserting values into the HashMap as the key, and 1 as their value. If the key
    # already exists, increment its value to track the number of occurrences.
    for key in range(da.length()):
        if map.contains_key(da[key]) is True:
            map.put(da[key], map.get(da[key]) + 1)
        else:
            map.put(da[key], 1)

        # Keep track of the highest frequency and mode values DA. If the current value is equal to the high frequency,
        # add the value to the value DA. If frequency exceeds the count, create a new DA with only the current value.
        if map.get(da[key]) == count:
            mode_da.append(da[key])
        if map.get(da[key]) > count:
            mode_da = DynamicArray()
            mode_da.append(da[key])
            count = map.get(da[key])

    # create tuple and return
    mode_tuple = (mode_da, count)
    return mode_tuple

# ------------------- BASIC TESTING ---------------------------------------- #


if __name__ == "__main__":

    print("\nPDF - put example 1")
    print("-------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put('str' + str(i), i * 100)
        if i % 25 == 24:
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())
    #
    print("\nPDF - put example 2")
    print("-------------------")
    m = HashMap(41, hash_function_2)
    for i in range(50):
        m.put('str' + str(i // 3), i * 100)
        if i % 10 == 9:
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())
    # #
    # print("\nPDF - resize Gradescope 2")
    # print("-------------------")
    # m = HashMap(10, hash_function_1)
    # m.put("key740", -726)
    # m.put("key454", 19)
    # m.put("key608", 596)
    # m.put("key79", -737)
    # m.put("key907", 555)
    # m.put("key808", -297)
    # m.put("key574", 853)
    # m.put("key783", -8)
    # m.put("key894", -542)
    # m.put("key939", -339)
    # m.put("key501", -852)
    # m.put("key601", 439)
    # print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())
    # m.resize_table(1)
    # print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())
    #
    # print("\nPDF - resize example 1")
    # print("----------------------")
    # m = HashMap(20, hash_function_1)
    # m.put('key1', 10)
    # print(m.get_size(), m.get_capacity(), m.get('key1'), m.contains_key('key1'))
    # m.resize_table(30)
    # print(m.get_size(), m.get_capacity(), m.get('key1'), m.contains_key('key1'))
    #
    # print("\nPDF - resize example 2")
    # print("----------------------")
    # m = HashMap(75, hash_function_2)
    # keys = [i for i in range(1, 1000, 13)]
    # for key in keys:
    #     m.put(str(key), key * 42)
    # print(m.get_size(), m.get_capacity())
    #
    # for capacity in range(111, 1000, 117):
    #     m.resize_table(capacity)
    #
    #     m.put('some key', 'some value')
    #     result = m.contains_key('some key')
    #     m.remove('some key')
    #
    #     for key in keys:
    #         # all inserted keys must be present
    #         result &= m.contains_key(str(key))
    #         # NOT inserted keys must be absent
    #         result &= not m.contains_key(str(key + 1))
    #     print(capacity, result, m.get_size(), m.get_capacity(), round(m.table_load(), 2))
    #
    # print("\nPDF - table_load example 1")
    # print("--------------------------")
    # m = HashMap(101, hash_function_1)
    # print(round(m.table_load(), 2))
    # m.put('key1', 10)
    # print(round(m.table_load(), 2))
    # m.put('key2', 20)
    # print(round(m.table_load(), 2))
    # m.put('key1', 30)
    # print(round(m.table_load(), 2))
    #
    # print("\nPDF - table_load example 2")
    # print("--------------------------")
    # m = HashMap(53, hash_function_1)
    # for i in range(50):
    #     m.put('key' + str(i), i * 100)
    #     if i % 10 == 0:
    #         print(round(m.table_load(), 2), m.get_size(), m.get_capacity())
    #
    # print("\nPDF - empty_buckets example 1")
    # print("-----------------------------")
    # m = HashMap(101, hash_function_1)
    # print(m.empty_buckets(), m.get_size(), m.get_capacity())
    # m.put('key1', 10)
    # print(m.empty_buckets(), m.get_size(), m.get_capacity())
    # m.put('key2', 20)
    # print(m.empty_buckets(), m.get_size(), m.get_capacity())
    # m.put('key1', 30)
    # print(m.empty_buckets(), m.get_size(), m.get_capacity())
    # m.put('key4', 40)
    # print(m.empty_buckets(), m.get_size(), m.get_capacity())
    # #
    # print("\nPDF - empty_buckets example 2")
    # print("-----------------------------")
    # m = HashMap(53, hash_function_1)
    # for i in range(150):
    #     m.put('key' + str(i), i * 100)
    #     if i % 30 == 0:
    #         print(m.empty_buckets(), m.get_size(), m.get_capacity())

    # print("\nPDF - get example 1")
    # print("-------------------")
    # m = HashMap(31, hash_function_1)
    # print(m.get('key'))
    # m.put('key1', 10)
    # print(m.get('key1'))
    #
    # print("\nPDF - get example 2")
    # print("-------------------")
    # m = HashMap(151, hash_function_2)
    # for i in range(200, 300, 7):
    #     m.put(str(i), i * 10)
    # print(m.get_size(), m.get_capacity())
    # for i in range(200, 300, 21):
    #     print(i, m.get(str(i)), m.get(str(i)) == i * 10)
    #     print(i + 1, m.get(str(i + 1)), m.get(str(i + 1)) == (i + 1) * 10)
    #
    # print("\nPDF - contains_key example 1")
    # print("----------------------------")
    # m = HashMap(53, hash_function_1)
    # print(m.contains_key('key1'))
    # m.put('key1', 10)
    # m.put('key2', 20)
    # m.put('key3', 30)
    # print(m.contains_key('key1'))
    # print(m.contains_key('key4'))
    # print(m.contains_key('key2'))
    # print(m.contains_key('key3'))
    # m.remove('key3')
    # print(m.contains_key('key3'))
    #
    # print("\nPDF - contains_key example 2")
    # print("----------------------------")
    # m = HashMap(79, hash_function_2)
    # keys = [i for i in range(1, 1000, 20)]
    # for key in keys:
    #     m.put(str(key), key * 42)
    # print(m.get_size(), m.get_capacity())
    # result = True
    # for key in keys:
    #     # all inserted keys must be present
    #     result &= m.contains_key(str(key))
    #     # NOT inserted keys must be absent
    #     result &= not m.contains_key(str(key + 1))
    # print(result)

    # print("\nPDF - remove example 1")
    # print("----------------------")
    # m = HashMap(53, hash_function_1)
    # print(m.get('key1'))
    # m.put('key1', 10)
    # print(m.get('key1'))
    # m.remove('key1')
    # print(m.get('key1'))
    # m.remove('key4')
    #
    # print("\nPDF - get_keys_and_values example 1")
    # print("------------------------")
    # m = HashMap(11, hash_function_2)
    # for i in range(1, 6):
    #     m.put(str(i), str(i * 10))
    # print(m.get_keys_and_values())
    #
    # m.put('20', '200')
    # m.remove('1')
    # m.resize_table(2)
    # print(m.get_keys_and_values())
    #
    # print("\nPDF - clear example 1")
    # print("---------------------")
    # m = HashMap(101, hash_function_1)
    # print(m.get_size(), m.get_capacity())
    # m.put('key1', 10)
    # m.put('key2', 20)
    # m.put('key1', 30)
    # print(m.get_size(), m.get_capacity())
    # m.clear()
    # print(m.get_size(), m.get_capacity())
    #
    # print("\nPDF - clear example 2")
    # print("---------------------")
    # m = HashMap(53, hash_function_1)
    # print(m.get_size(), m.get_capacity())
    # m.put('key1', 10)
    # print(m.get_size(), m.get_capacity())
    # m.put('key2', 20)
    # print(m.get_size(), m.get_capacity())
    # m.resize_table(100)
    # print(m.get_size(), m.get_capacity())
    # m.clear()
    # print(m.get_size(), m.get_capacity())
    #
    # print("\nPDF - find_mode example 1")
    # print("-----------------------------")
    # da = DynamicArray(["apple", "apple", "grape", "melon", "peach"])
    # mode, frequency = find_mode(da)
    # print(f"Input: {da}\nMode : {mode}, Frequency: {frequency}")
    #
    # print("\nPDF - find_mode example 2")
    # print("-----------------------------")
    # test_cases = (
    #     ["Arch", "Manjaro", "Manjaro", "Mint", "Mint", "Mint", "Ubuntu", "Ubuntu", "Ubuntu"],
    #     ["one", "two", "three", "four", "five"],
    #     ["2", "4", "2", "6", "8", "4", "1", "3", "4", "5", "7", "3", "3", "2"]
    # )
    #
    # for case in test_cases:
    #     da = DynamicArray(case)
    #     mode, frequency = find_mode(da)
    #     print(f"Input: {da}\nMode : {mode}, Frequency: {frequency}\n")
