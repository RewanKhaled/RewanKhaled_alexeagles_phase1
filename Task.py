#!/usr/bin/env python3
import cv2 as cv
import numpy as np
from typing import Tuple
from fixed_values import inner_diameter_normal_size, minimum_value_missing_teeth, maximum_value_missing_teeth, valid_choices
import sys

def filtering_small_contours(all_contours: Tuple[np.ndarray]) -> list:
    """
    Filters and returns large contours that represent worn or missing teeth or the diameter of the gear.
    """
    long_difference_contours = []
    for contour in all_contours:
        if len(contour) >= 15:
            long_difference_contours.append(contour)
    return long_difference_contours

def checking_contour_type(contours: list[np.ndarray], worn_teeth_count: int, missing_teeth_count: int) -> Tuple[int, int]:
    """
    Checks and counts worn and missing teeth based on contour area.
    """
    for contour in contours:
        contour_area = cv.contourArea(contour)
        if minimum_value_missing_teeth <= contour_area <= maximum_value_missing_teeth:
            missing_teeth_count += 1
        else:
            worn_teeth_count += 1
    return worn_teeth_count, missing_teeth_count

def checking_inner_diameter_condition(ideal: np.ndarray, worn_sample: np.ndarray, blank: np.ndarray) -> Tuple[str, np.ndarray]:
    """
    Evaluates the condition of the inner diameter and returns its status and the XORed difference.
    """
    _, thresh_ideal = cv.threshold(ideal, 90, 255, cv.THRESH_BINARY)
    _, thresh_worn = cv.threshold(worn_sample, 90, 255, cv.THRESH_BINARY)
    difference = cv.bitwise_xor(thresh_ideal, thresh_worn)
    difference_contour, _ = cv.findContours(difference, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    cv.drawContours(blank, difference_contour, -1, (0, 0, 255), 1)
    try:
        contour_area = cv.contourArea(difference_contour[0])
    except IndexError:
        return 'Normal', None

    if contour_area == inner_diameter_normal_size:
        return 'Missing', difference
    elif contour_area > inner_diameter_normal_size:
        return 'Bigger', difference
    else:
        return 'Smaller', difference

def taking_user_input() -> str:
    """
    Takes user input to select which sample image to use.
    """
    with open('./task_images/Samples Description.txt', 'r', encoding='utf8') as file:
        lines = file.readlines()
        for line in lines[1:]:
            print(line, end='')
        print('')
    print('Which sample do you want to try: ', end='')
    choice = input()
    if int(choice) in valid_choices:
        return f'./task_images/sample{choice}.jpg'
    else:
        print('Invalid sample number')
        sys.exit(1)

if __name__ == '__main__':
    
    # Load the ideal and user-selected test images
    reference_img = cv.imread('./task_images/ideal.jpg')
    test_img = cv.imread(taking_user_input())
    
    # Create blank canvases for drawing
    blank_reference = np.zeros(reference_img.shape, dtype='uint8')
    blank_test = np.zeros(reference_img.shape, dtype='uint8')
    blank_difference = np.zeros(reference_img.shape, dtype='uint8')
    inner_diameter_mask_blank = np.zeros(reference_img.shape[:2], dtype='uint8')

    # Convert images to grayscale
    ref_img_gray = cv.cvtColor(reference_img, cv.COLOR_BGR2GRAY)
    test_img_gray = cv.cvtColor(test_img, cv.COLOR_BGR2GRAY)

    # Create a circular mask to isolate the inner diameter
    mask_center = (reference_img.shape[1] // 2, reference_img.shape[0] // 2)
    mask_radius = 110
    mask = cv.circle(inner_diameter_mask_blank, mask_center, mask_radius, 255, -1)
    inverted_mask = cv.bitwise_not(mask)

    masked_ref_img = cv.bitwise_and(ref_img_gray, ref_img_gray, mask=mask)
    masked_test_img = cv.bitwise_and(test_img_gray, test_img_gray, mask=mask)
    inverted_masked_ref_img = cv.bitwise_and(ref_img_gray, ref_img_gray, mask=inverted_mask)
    inverted_masked_test_img = cv.bitwise_and(test_img_gray, test_img_gray, mask=inverted_mask)

    # Evaluate the inner diameter condition
    diameter_status, inner_diameter_difference = checking_inner_diameter_condition(masked_ref_img, masked_test_img, blank_difference)

    # Apply adaptive thresholding
    threshold_ref = cv.adaptiveThreshold(inverted_masked_ref_img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
    threshold_test = cv.adaptiveThreshold(inverted_masked_test_img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)

    # Find differences between images using XOR operation
    difference_img = cv.bitwise_xor(threshold_ref, threshold_test)
    overall_difference_img = difference_img.copy()
    if diameter_status != 'Normal':
        overall_difference_img = cv.bitwise_or(difference_img, inner_diameter_difference)

    # Find contours in the thresholded images
    contours_ref, _ = cv.findContours(threshold_ref, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contours_test, _ = cv.findContours(threshold_test, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    difference_contours, _ = cv.findContours(difference_img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # Filter out insignificant contours
    significant_diff_contours = filtering_small_contours(difference_contours)

    # Draw contours on the blank canvases
    cv.drawContours(blank_reference, contours_ref, -1, (255, 0, 0), 2)
    cv.drawContours(blank_test, contours_test, -1, (255, 0, 0), 2)
    cv.drawContours(blank_difference, significant_diff_contours, -1, (0, 0, 255), 2)

    # Classify the contours to count worn and missing teeth
    worn_teeth_count, missing_teeth_count = checking_contour_type(significant_diff_contours, 0, 0)

    # Display the results
    print(f'Number of missing teeth: {missing_teeth_count}')
    print('-------------------')
    print(f'Number of worn teeth: {worn_teeth_count}')
    print('-------------------')
    print(f'The condition of the inner diameter is: {diameter_status}')

    # Show the difference images
    cv.imshow('Overall Difference', overall_difference_img)
    cv.imshow('Significant Difference Contours', blank_difference)
    cv.waitKey(0)
