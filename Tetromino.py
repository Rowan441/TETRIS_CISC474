from Point import Point 
from typing import TypedDict

class RotatedTetromino(TypedDict):
    bottom_points: list[Point]
    points: list[Point]
    

class Tetrominos(TypedDict):
    up: RotatedTetromino
    right: RotatedTetromino
    left: RotatedTetromino
    down: RotatedTetromino
    num_rotations: int

PIECES: dict[str, Tetrominos] = {
    "O": {
        "up" : {
            'points': [
                Point(0, 0),
                Point(1, 0),
                Point(0, 1),
                Point(1, 1),
            ]
        },
        "right" : {
            'points': [
                Point(0, 0),
                Point(1, 0),
                Point(0, 1),
                Point(1, 1),
            ]
        },
        "down" : {
            'points': [
                Point(0, 0),
                Point(1, 0),
                Point(0, 1),
                Point(1, 1),
            ]
        },
        "left" : {
            'points': [
                Point(0, 0),
                Point(1, 0),
                Point(0, 1),
                Point(1, 1),
            ]
        },
        "num_rotations": 1
    },
    "T": {
        "left" : {
            'points': [
                Point(0, 1),
                Point(1, 0),
                Point(1, 1),
                Point(1, 2),
            ]
        },
        "right" : {
            'points': [
                Point(1, 0),
                Point(1, 1),
                Point(1, 2),
                Point(2, 1),
            ]
        },
        "down" : {
            'points': [
                Point(0, 1),
                Point(1, 0),
                Point(1, 1),
                Point(2, 1),
            ]
        },
        "up" : {
            'points': [
                Point(0, 0),
                Point(1, 0),
                Point(1, 1),
                Point(2, 0),
            ]
        },
        "num_rotations": 4
    },
    "L1": {
        "right" : {
            'points': [
                Point(1, 0),
                Point(1, 1),
                Point(1, 2),
                Point(2, 0),
            ]
        },
        "left" : {
            'points': [
                Point(1, 0),
                Point(1, 1),
                Point(1, 2),
                Point(0, 2),
            ]
        },
        "down" : {
            'points': [
                Point(0, 0),
                Point(0, 1),
                Point(1, 1),
                Point(2, 1),
            ]
        },
        "up" : {
            'points': [
                Point(0, 0),
                Point(1, 0),
                Point(2, 0),
                Point(2, 1),
            ]
        },
        "num_rotations": 4
    },
    "L2": {
        "up" : {
            'points': [
                Point(0, 0),
                Point(0, 1),
                Point(1, 1),
                Point(2, 1),
            ]
        },
        "right" : {
            'points': [
                Point(1, 0),
                Point(1, 1),
                Point(1, 2),
                Point(2, 2),
            ]
        },
        "down" : {
            'points': [
                Point(0, 1),
                Point(1, 1),
                Point(2, 1),
                Point(2, 0),
            ]
        },
        "left" : {
            'points': [
                Point(0, 0),
                Point(1, 0),
                Point(1, 1),
                Point(1, 2)
            ]
        },
        "num_rotations": 2
    },
    "I": {
        "left" : {
            'points': [
                Point(0, 2),
                Point(1, 2),
                Point(2, 2),
                Point(3, 2),
            ]
        },
        "right" : {
            'points': [
                Point(0, 2),
                Point(1, 2),
                Point(2, 2),
                Point(3, 2),
            ]
        },
        "down" : {
            'points': [
                Point(2, 0),
                Point(2, 1),
                Point(2, 2),
                Point(2, 3),
            ]
        },
        "up" : {
            'points': [
                Point(2, 0),
                Point(2, 1),
                Point(2, 2),
                Point(2, 3),
            ]
        },
        "num_rotations": 2
    },
    "Z1": {
        "left" : {
            'points': [
                Point(0, 0),
                Point(1, 0),
                Point(1, 1),
                Point(2, 1),
            ]
        },
        "right" : {
            'points': [
                Point(0, 0),
                Point(1, 0),
                Point(1, 1),
                Point(2, 1),
            ]
        },
        "down" : {
            'points': [
                Point(0, 1),
                Point(0, 2),
                Point(1, 1),
                Point(1, 0),
            ]
        },
        "up" : {
            'points': [
                Point(0, 1),
                Point(0, 2),
                Point(1, 1),
                Point(1, 0),
            ]
        },
        "num_rotations": 2
    },
    "Z2": {
        "left" : {
            'points': [
                Point(0, 1),
                Point(1, 0),
                Point(1, 1),
                Point(2, 0),
            ]
        },
        "right" : {
            'points': [
                Point(0, 1),
                Point(1, 0),
                Point(1, 1),
                Point(2, 0),
            ]
        },
        "down" : {
            'points': [
                Point(1, 0),
                Point(1, 1),
                Point(2, 1),
                Point(2, 2),
            ]
        },
        "up" : {
            'points': [
                Point(1, 0),
                Point(1, 1),
                Point(2, 1),
                Point(2, 2),
            ]
        },
        "num_rotations": 2
    },
}

PIECES_NAMES = list(PIECES.keys())