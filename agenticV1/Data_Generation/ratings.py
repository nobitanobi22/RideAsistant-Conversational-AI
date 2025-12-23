import numpy as np

np.random.seed(42)

# Spread-out versions of each component
def left_pdf(x):
    return np.exp(-((x - 1.5) ** 2) / 1.5)  # wider spread

def main_pdf(x):
    return np.exp(-((x - 3.0) ** 2) / 0.8)

def right_pdf(x):
    return np.exp(-((x - 4.0) ** 2) / 1.3)

# Generic rejection sampler
def rejection_sampler(pdf_func, n_samples, xmin=0.01, xmax=4.99):
    x_vals = np.linspace(xmin, xmax, 1000)
    max_pdf = np.max(pdf_func(x_vals))

    samples = []
    while len(samples) < n_samples:
        x = np.random.uniform(xmin, xmax)
        y = np.random.uniform(0, max_pdf)
        if y < pdf_func(x):
            samples.append(x)
    return np.array(samples)

# Sample each component separately
n = 10000
left_samples = rejection_sampler(left_pdf, n)
main_samples = rejection_sampler(main_pdf, n)
right_samples = rejection_sampler(right_pdf, n)