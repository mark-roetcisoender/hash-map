# Name: Mark Roetcisoender
# OSU Email: roetcism@oregonstate.edu
# Course: CS261 - Data Structures
# Assignment: Assignment 6
# Due Date: 3/14/2024
# Description: An implementation of HashMap using Open Addressing with Quadratic Probing.

from a6_include import (DynamicArray, DynamicArrayException, HashEntry, hash_function_1, hash_function_2)


class HashMap:
    def __init__(self, capacity: int, function) -> None:
        """
        Initialize new HashMap that uses
        quadratic probing for collision resolution
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        self._buckets = DynamicArray()

        # capacity must be a prime number
        self._capacity = self._next_prime(capacity)
        for _ in range(self._capacity):
            self._buckets.append(None)

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
        Increment from given number to find the closest prime number
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
        Takes a key/value pair as separate parameters and inserts them into the hash map. If the key already exists, in
        the hash map, the value is updated at the key's current location. If the table load exceeds .5, the hash map
        is resized to double its current capacity. Utilizes an indirect recursive call of resize()
        """
        # check if the table load is greater than or equal to .5 & call resize if so
        if self.table_load() >= .5:
            self.resize_table(self._capacity * 2)

        # find the index to insert the value at
        hashed_key = self._hash_function(key)
        index = hashed_key % self._capacity
        quad_num = 1

        # check if the key exists already in the hash map and replace its value if so. Find its index and quadratically
        # probe until the key is found. Make sure to update TS values if need be. Return once done
        if self.contains_key(key) is True:
            while self._buckets[index].key != key:
                index = (hashed_key + (quad_num * quad_num)) % self._capacity
                quad_num += 1
                if self._buckets[index].is_tombstone is True:
                    self._buckets[index].is_tombstone = False
                    self._size += 1
            self._buckets[index].value = value
            return

        # if there is a non-TS value at our index, quadratically probe until we reach a valid slot
        while self._buckets[index] is not None and self._buckets[index].is_tombstone is False:
            index = (hashed_key + (quad_num * quad_num)) % self._capacity
            quad_num += 1

        # insert the new key/value, increment the size, and if the insert location was a TS, change TS value to False
        self._buckets[index] = HashEntry(key, value)
        self._size += 1
        if self._buckets[index].is_tombstone is True:
            self._buckets[index].is_tombstone = False

    def resize_table(self, new_capacity: int) -> None:
        """
        Updates the capacity of the underlying table in the hash map. Takes an integer as a parameter and uses that as
        the new capacity. If the integer is not prime, updates it to be the next prime number.  If the parameter is
        less than the current size of the hash map, the method does nothing. Utilizes an indirect recursive call of
        put()
        """
        # check if the new_capacity is less than the current size
        if new_capacity < self._size:
            return

        # create DA of keys and values prior to changing capacity of the hash map
        temp_array = self.get_keys_and_values()

        # check if the new_capacity is prime. If not, assign it to be the next prime number. Update the hash map's
        # capacity
        if self._is_prime(new_capacity) is False:
            new_capacity = self._next_prime(new_capacity)
        self._capacity = new_capacity

        # Update self._buckets to be a fresh DA, and append it to be the new capacity. Update size to 0
        self._buckets = DynamicArray()
        for x in range(self._capacity):
            self._buckets.append(None)
        self._size = 0

        # Iterate through entries in the key/value DA & re-hash the keys using put()
        for _ in range(temp_array.length()):
            self.put(temp_array[_][0], temp_array[_][1])

    def table_load(self) -> float:
        """
        Returns the table load of the hash map (number of valid elements/ capacity of the hash table).
        """
        return self._size / self._capacity

    def empty_buckets(self) -> int:
        """
        Returns an integer representing the number of empty buckets in the hashmap
        """
        # establish a counter, and iterate through the hashmap. If the bucket is empty, or a TS, increment the count
        count = 0
        for _ in range(self._buckets.length()):
            if self._buckets[_] is None or self._buckets[_].is_tombstone is True:
                count += 1
        return count

    def get(self, key: str) -> object:
        """
        Returns the value associated with the parameter key. Returns None if the key doesn't exist in the hashmap
        """
        # see if the key is in the hashmap
        if self.contains_key(key) is False:
            return None

        # find the index the key hashes to
        hashed_key = self._hash_function(key)
        index = hashed_key % self._capacity
        quad_num = 1

        # since we know the key is in the hashmap, quadratically probe until we find it & return its value
        while self._buckets[index].key != key:
            index = (hashed_key + quad_num * quad_num) % self._capacity
            quad_num += 1

        return self._buckets[index].value

    def contains_key(self, key: str) -> bool:
        """
        Takes a key as a parameter and searches the hashmap for it. Returns True if the key exists in the hashmap
        and False otherwise
        """
        # if the size of the hashmap is 0, we know it's empty
        if self._size == 0:
            return False

        # determine where the key hashes to. If it's empty, return False
        hashed_key = self._hash_function(key)
        index = hashed_key % self._capacity
        quad_num = 1
        if self._buckets[index] is None:
            return False

        # # if the index contains the key and isn't a TS, return True
        if self._buckets[index].key == key and self._buckets[index].is_tombstone is False:
            return True

        # if the index isn't empty or is a TS, probe quadratically.
        while self._buckets[index] is not None or self._buckets[index].is_tombstone is True:
            index = (hashed_key + quad_num * quad_num) % self._capacity
            quad_num += 1
            # If we find a None entry, return False
            if self._buckets[index] is None:
                return False
            # if we've found the value, but it's TS, return False
            if self._buckets[index].key == key and self._buckets[index].is_tombstone is True:
                return False
            # if we find the value, return True
            if self._buckets[index].key == key:
                return True
        return False

    def remove(self, key: str) -> None:
        """
        Takes a key as a parameter and removes it, and it's associate value from the hashmap by updating its TS value
        to True. If the key is not in the hash map, nothing is done.
        """
        # if the key isn't in the hashmap, return
        if self.contains_key(key) is False:
            return

        # determine the index.
        hashed_key = self._hash_function(key)
        index = hashed_key % self._capacity
        quad_num = 1

        # if we've found the key, but it's a TS, return
        if self._buckets[index].key == key and self._buckets[index].is_tombstone is True:
            return
        # If the key is not at the index, or we're at a TS, quadratically probe until we find the key
        while self._buckets[index].key != key or self._buckets[index].is_tombstone is True:
            index = (hashed_key + quad_num * quad_num) % self._capacity
            quad_num += 1
            # if we've found the key, but it's a TS, return
            if self._buckets[index].key == key and self._buckets[index].is_tombstone is True:
                return

        # if we're here, we've found the key & it's not a TA. Update TS value to True and decrement size of hashmap
        self._buckets[index].is_tombstone = True
        self._size -= 1

    def get_keys_and_values(self) -> DynamicArray:
        """
        Returns a dynamic array containing the key-value pairs from the hashmap in tuples.
        """
        return_da = DynamicArray()
        # Iterate through self._buckets, and if there is a value, and it's not a tombstone, add it's key and value to
        # return DA.
        for _ in range(self._capacity):
            if self._buckets[_] is not None and self._buckets[_].is_tombstone is False:
                a_tuple = (self._buckets[_].key, self._buckets[_].value)
                return_da.append(a_tuple)
        return return_da

    def clear(self) -> None:
        """
        Clears the contents of the hashmap by re-initializing each value in the bucket DA to None. Does not effect
        the capacity of the hashmap.
        """
        for _ in range(self._capacity):
            self._buckets[_] = None
        self._size = 0

    def update_value(self, key, value):
        """Helper method to update a key's value"""

    def __iter__(self):
        """
        Iterator class built within the hash map to enable iteration
        """
        self._index = 0
        return self

    def __next__(self):
        """
        Returns the next method in the hash map based on where the iterator value is currently. Checks if the value
        is None or is a tombstone, and advances until a valid value is reached.
        """
        try:
            while self._buckets[self._index] is None or self._buckets[self._index].is_tombstone is True:
                self._index = self._index + 1
            value = self._buckets[self._index]
        except DynamicArrayException:
            raise StopIteration
        self._index = self._index + 1
        return value


# ------------------- BASIC TESTING ---------------------------------------- #

if __name__ == "__main__":

    print("\nPDF - put example 1")
    print("-------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put('str' + str(i), i * 100)
        if i % 25 == 24:
            # print(m)
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())
    # print(m)

    # print("\nPDF - put example 1")
    # print("-------------------")
    # m = HashMap(53, hash_function_1)
    # for i in range(27):
    #     m.put('str' + str(i), i * 100)
    #     if i % 25 == 24:
    #         print(m)
    #         print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())
    # print(m)
    # m.put('str27', 2700)
    # print(m)
    # print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())

    # print(m)
    # #
    # print("\nPDF - put example 2")
    # print("-------------------")
    # m = HashMap(41, hash_function_2)
    # for i in range(50):
    #     m.put('str' + str(i // 3), i * 100)
    #     if i % 10 == 9:
    #         print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())
    # # print(m)
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
    # keys = [i for i in range(25, 1000, 13)]
    # for key in keys:
    #     m.put(str(key), key * 42)
    # print(m.get_size(), m.get_capacity())
    # # print(m)
    #
    # for capacity in range(111, 1000, 117):
    #     m.resize_table(capacity)
    #
    #     if m.table_load() > 0.5:
    #         print(f"Check that the load factor is acceptable after the call to resize_table().\n"
    #               f"Your load factor is {round(m.table_load(), 2)} and should be less than or equal to 0.5")
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
    # print("\nPDF - resize example 2")
    # print("----------------------")
    # m = HashMap(75, hash_function_2)
    # keys = [i for i in range(25, 1000, 13)]
    # for key in keys:
    #     m.put(str(key), key * 42)
    # print(m.get_size(), m.get_capacity())
    # # print(m)
    #
    # for capacity in range(111, 1000, 117):
    #     m.resize_table(capacity)
    #     # print(m)
    #
    #     if m.table_load() > 0.5:
    #         print(f"Check that the load factor is acceptable after the call to resize_table().\n"
    #               f"Your load factor is {round(m.table_load(), 2)} and should be less than or equal to 0.5")
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
    #
    # print("\nPDF - get example 1")
    # print("-------------------")
    # m = HashMap(31, hash_function_1)
    # print(m.get('key'))
    # m.put('key1', 10)
    # print(m.get('key1'))
    # #
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
    # m = HashMap(11, hash_function_1)
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
    # # #
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
    #
    # print("\nPDF - remove example 1")
    # print("----------------------")
    # m = HashMap(53, hash_function_1)
    # print(m.get('key1'))
    # m.put('key1', 10)
    # print(m.get('key1'))
    # m.remove('key1')
    # print(m.get('key1'))
    # m.remove('key4')
    # #
    # print("\nPDF - get_keys_and_values example 1")
    # print("------------------------")
    # m = HashMap(11, hash_function_2)
    # for i in range(1, 6):
    #     m.put(str(i), str(i * 10))
    # print(m.get_keys_and_values())
    #
    # m.resize_table(2)
    # print(m.get_keys_and_values())
    #
    # m.put('20', '200')
    # m.remove('1')
    # m.resize_table(12)
    # print(m.get_keys_and_values())
    # # #
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
    # #
    # print("\nPDF - __iter__(), __next__() example 1")
    # print("---------------------")
    # m = HashMap(10, hash_function_1)
    # for i in range(5):
    #     m.put(str(i), str(i * 10))
    # print(m)
    # for item in m:
    #     print('K:', item.key, 'V:', item.value)
    #
    # print("\nPDF - __iter__(), __next__() example 2")
    # print("---------------------")
    # m = HashMap(10, hash_function_2)
    # for i in range(5):
    #     m.put(str(i), str(i * 24))
    # m.remove('0')
    # m.remove('4')
    # print(m)
    # for item in m:
    #     print('K:', item.key, 'V:', item.value)
