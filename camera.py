import cv2
import numpy as np
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def canvas(h, w):
    return np.zeros((h, w, 3))


def get_model_mat(angle):
    angle *= np.pi / 180
    return np.array(
        [
            [np.cos(angle), -np.sin(angle), 0, 0],
            [np.sin(angle), np.cos(angle), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]
    )


def get_view_mat(eye_pose):
    return np.array(
        [
            [1, 0, 0, -eye_pose[0]],
            [0, 1, 0, -eye_pose[1]],
            [0, 0, 1, -eye_pose[2]],
            [0, 0, 0, 1],
        ]
    )


def get_proj_mat(fov, aspect, near, far):
    t2a = np.tan(fov / 2.0)
    return np.array(
        [
            [1 / (aspect * t2a), 0, 0, 0],
            [0, 1 / t2a, 0, 0],
            [0, 0, (near + far) / (near - far), 2 * near * far / (near - far)],
            [0, 0, -1, 0],
        ]
    )


def get_viewport_mat(h, w):
    return np.array(
        [[w / 2, 0, 0, w / 2], [0, h / 2, 0, h / 2], [0, 0, 1, 0], [0, 0, 0, 1]]
    )

def get_world2view_mat(R, t, translate=np.array([0.0, 0.0, 0.0]), scale=1.0):
    Rt = np.zeros((4, 4))
    Rt[:3, :3] = R.transpose()
    Rt[:3, 3] = t
    Rt[3, 3] = 1.0

    c2w = np.linalg.inv(Rt)
    cam_center = c2w[:3, 3]
    cam_center = (cam_center + translate) * scale
    c2w[:3, 3] = cam_center
    Rt = np.linalg.inv(c2w)
    return np.float32(Rt)


def get_proj_mat_J(znear, zfar, fovX, fovY):
    tanHalfFovY = math.tan((fovY / 2))
    tanHalfFovX = math.tan((fovX / 2))

    top = tanHalfFovY * znear
    bottom = -top
    right = tanHalfFovX * znear
    left = -right

    P = np.zeros((4, 4))

    z_sign = 1.0

    P[0, 0] = 2.0 * znear / (right - left)
    P[1, 1] = 2.0 * znear / (top - bottom)
    P[0, 2] = (right + left) / (right - left)
    P[1, 2] = (top + bottom) / (top - bottom)
    P[3, 2] = z_sign
    P[2, 2] = z_sign * zfar / (zfar - znear)
    P[2, 3] = -(zfar * znear) / (zfar - znear)
    return P

if __name__ == "__main__":
    frame = canvas(700, 700)
    angle = 0
    eye = [0, 0, 5]
    pts = [[2, 0, -2], [0, 2, -2], [-2, 0, -2]]
    viewport = get_viewport_mat(700, 700)

    mvp = get_model_mat(angle)
    mvp = np.dot(get_view_mat(eye), mvp)
    mvp = np.dot(get_proj_mat(45, 1, 0.1, 50), mvp)

    pts_2d = []
    for p in pts:
        p = np.array(p + [1])
        p = np.dot(mvp, p)
        p /= p[3]

        p = np.dot(viewport, p)[:2]
        pts_2d.append([int(p[0]), int(p[1])])

    vis = 1
    if vis:
        fig = plt.figure()
        pts = np.array(pts)
        x, y, z = pts[:, 0], pts[:, 1], pts[:, 2]

        ax = Axes3D(fig)
        ax.scatter(x, y, z, s=80, marker="^", c="g")
        ax.scatter([eye[0]], [eye[1]], [eye[2]], s=180, marker=7, c="r")
        ax.plot_trisurf(x, y, z, linewidth=0.2, antialiased=True, alpha=0.5)
        plt.show()

        c = (255, 255, 255)
        for i in range(3):
            for j in range(i + 1, 3):
                cv2.line(frame, pts_2d[i], pts_2d[j], c, 2)
        cv2.imshow("screen", frame)
        cv2.waitKey(0)