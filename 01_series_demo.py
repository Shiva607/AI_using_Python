import pandas as pd
import matplotlib.pyplot as plt

#! video Reference: https://www.youtube.com/watch?v=vtgDGrUiUKk
#! Documentation: https://medium.com/@sathishkumar.babu89/pandas-series-the-one-dimensional-workhorse-youll-use-every-day-4628e8a1f6e2
#! Notes: https://colab.research.google.com/drive/1vsANmljtPHhElyS9gOHo1cTsmBkpa9LE?usp=sharing 

# The Pandas Series is an essential building block for data analysis and manipulation.

# Its labeled indexing, vectorized operations, missing data handling, performance optimizations, and integration with other libraries make it a powerful tool, especially when working with large and structured datasets. Whether you're handling time series, working with numerical data, or performing complex analysis, Series provide a flexible and efficient structure for all your data needs.


# 1. Labeled Indexing
series = pd.Series([10, 20, 30], index=["a", "b", "c"])
print("Pandas Series - Access using label")
print(series["b"])  # Access using label

# 2. Handling Missing Data 
# Pandas Series can handle missing data more gracefully using functions like isna(), fillna(), and dropna(). Missing values are often represented as NaN (Not a Number), and Pandas provides built-in methods to handle these missing values

missing_series = pd.Series([10, 20, None, 40])
series_filled = missing_series.fillna(0)  # Fill missing values with 0
print("Pandas Series - Fill missing values with 0")
print(series_filled)

# 3. Vectorized Operations
# you can apply mathematical or logical operations to the entire Series without the need for explicit loops, leading to faster execution and cleaner code

vector_series = pd.Series([10, 20, 30])
result = vector_series + 5  # Adds 5 to every element
print("Pandas Series - Adds 5 to every element")
print(result)

# 4. Flexible Data Types
multiple_data = [10, "Hello", 3.14, True]
series_ml = pd.Series(multiple_data)

# Printing the Series
print("Pandas Series with multiple data types:")
print(series_ml)

# 5. Alignment of Data
# If you add two Series with the same or different indices, Pandas automatically aligns them based on the index and handles missing values accordingly

series1 = pd.Series([10, 20, 30], index=["a", "b", "c"])
series2 = pd.Series([5, 15, 25], index=["b", "a", "c"])
Alignment_result = series1 + series2
print(Alignment_result)

# 6. Integration with Other Libraries
# Series is well-integrated with many other libraries in the Python ecosystem, especially NumPy, Matplotlib, and SciPy

series = pd.Series([10, 20, 30, 40])
series.plot(kind='bar')  # Create a bar plot
plt.show()