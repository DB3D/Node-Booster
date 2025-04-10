# SPDX-FileCopyrightText: 2025 BD3D DIGITAL DESIGN (Dorian B.)
#
# SPDX-License-Identifier: GPL-2.0-or-later

# NOTE 
# this is a numpy library for working with 2D bezier curves and interpolation.
# heavily related to blender mapping.curve API.

# NOTE 
# about AI
# gemini 2.5 helped heavily here. Very good with numpy math. incredible. 
# Make sure you observe if his logic is valid tho..


import numpy as np
import hashlib


def reverseengineer_curvemapping_to_bezsegs(curve) -> np.ndarray:
    """
    Convert a Blender CurveMapping object to a NumPy array of Bézier segments,
    calculating handle positions based on Blender's internal C functions,
    optionally ensuring X-monotonicity.
    Returns: np.ndarray: An (N-1) x 8 NumPy array [P0x, P0y, P1x, P1y, P2x, P2y, P3x, P3y].
    """

    # NOTE
    # a blender curvemapping bezier has a lot of logic to it with the handles.
    # this function tries to reverse engineer that logic into a list of cubic beziers segments.
    # could be largly improved and cleaned up.

    def _guess_handles(current_pt, prev_pt, next_pt):
        """Calculates handle positions mimicking Blender C function calchandle_curvemap."""

        handle_type = current_pt.handle_type
        h1_type = handle_type
        h2_type = handle_type

        p2 = np.array(current_pt.location, dtype=float)

        if (prev_pt is None):
            if (next_pt is None):
                p1 = p2.copy(); p3 = p2.copy()
            else:
                p3 = np.array(next_pt.location, dtype=float)
                p1 = 2.0 * p2 - p3
        else:
            p1 = np.array(prev_pt.location, dtype=float)
            if (next_pt is None):
                p3 = 2.0 * p2 - p1
            else:
                p3 = np.array(next_pt.location, dtype=float)

        dvec_a = np.subtract(p2, p1)
        dvec_b = np.subtract(p3, p2)
        len_a = np.linalg.norm(dvec_a)
        len_b = np.linalg.norm(dvec_b)

        if (abs(len_a) < 1e-5): len_a = 1.0
        if (abs(len_b) < 1e-5): len_b = 1.0

        h1_calc = p2.copy()
        h2_calc = p2.copy()

        if ((h1_type == 'AUTO') or (h1_type == 'AUTO_CLAMPED')):
            tvec = (dvec_b / len_b) + (dvec_a / len_a)
            len_tvec = np.linalg.norm(tvec)
            len_factor = len_tvec * 2.5614

            if (abs(len_factor) > 1e-5):
                scale_a = len_a / len_factor
                scale_b = len_b / len_factor
                base_h1 = p2 - tvec * scale_a
                base_h2 = p2 + tvec * scale_b
                h1_calc = base_h1.copy()
                h2_calc = base_h2.copy()

                if ((h1_type == 'AUTO_CLAMPED') and (prev_pt is not None) and (next_pt is not None)):
                    y_prev = prev_pt.location[1]
                    y_curr = current_pt.location[1]
                    y_next = next_pt.location[1]
                    ydiff1 = y_prev - y_curr
                    ydiff2 = y_next - y_curr
                    is_extremum = (ydiff1 <= 0.0 and ydiff2 <= 0.0) or \
                                  (ydiff1 >= 0.0 and ydiff2 >= 0.0)
                    if (is_extremum):
                        h1_calc[1] = y_curr
                    else:
                        if ydiff1 <= 0.0: h1_calc[1] = max(y_prev, base_h1[1])
                        else: h1_calc[1] = min(y_prev, base_h1[1])

                if ((h2_type == 'AUTO_CLAMPED') and (prev_pt is not None) and (next_pt is not None)):
                    y_prev = prev_pt.location[1]
                    y_curr = current_pt.location[1]
                    y_next = next_pt.location[1]
                    ydiff1 = y_prev - y_curr
                    ydiff2 = y_next - y_curr
                    is_extremum = (ydiff1 <= 0.0 and ydiff2 <= 0.0) or \
                                  (ydiff1 >= 0.0 and ydiff2 >= 0.0)
                    if (is_extremum):
                        h2_calc[1] = y_curr
                    else:
                        if (ydiff1 <= 0.0): h2_calc[1] = min(y_next, base_h2[1])
                        else: h2_calc[1] = max(y_next, base_h2[1])

        elif (h1_type == 'VECTOR'):
            h1_calc = p2 - dvec_a / 3.0
            h2_calc = p2 + dvec_b / 3.0

        if np.any(np.isnan(h1_calc)): h1_calc = p2.copy()
        if np.any(np.isnan(h2_calc)): h2_calc = p2.copy()

        return h1_calc, h2_calc

    def _points_x_monotonicity(points, all_left_h, all_right_h):
        """
        Adjusts calculated handle X-coordinates to ensure X-monotonicity for each segment.
        Enforces x0 <= x1 <= x2 <= x3 where P1=HR_i, P2=HL_i+1.

        Args:
            points: List of CurveMapPoint objects.
            all_left_h: List of calculated left handle positions (np.arrays).
            all_right_h: List of calculated right handle positions (np.arrays).

        Returns:
            tuple: (final_left_h, final_right_h) - Lists of adjusted handle positions.
        """
        n_points = len(points)
        if (n_points < 2):
            return list(all_left_h), list(all_right_h)

        # Create copies to modify
        final_left_h = [h.copy() for h in all_left_h]
        final_right_h = [h.copy() for h in all_right_h]

        # Iterate through segments [i, i+1]
        for i in range(n_points - 1):
            # P0 = knot[i], P1 = HR[i], P2 = HL[i+1], P3 = knot[i+1]
            x_k_i = points[i].location[0]
            x_k_i1 = points[i+1].location[0]
            # X-coords of handles relevant to this segment
            x_hr_i_orig = final_right_h[i][0]   # P1.x original
            x_hl_i1_orig = final_left_h[i+1][0] # P2.x original

            # Apply clamping based on x0 <= x1 <= x2 <= x3
            # 1. Clamp P1.x (x_hr_i) >= P0.x (x_k_i)
            x_hr_i_clamped = max(x_k_i, x_hr_i_orig)
            # 2. Clamp P2.x (x_hl_i1) <= P3.x (x_k_i1)
            x_hl_i1_clamped = min(x_k_i1, x_hl_i1_orig)
            # 3. Check for crossover: P1.x > P2.x after clamping
            if x_hr_i_clamped > x_hl_i1_clamped:
                # Crossover occurred. Handles need to meet.
                # Calculate the midpoint of the conflicting interval.
                x_split = (x_hr_i_clamped + x_hl_i1_clamped) / 2.0
                # Ensure the split point is strictly within the knot interval.
                x_split = max(x_k_i, min(x_k_i1, x_split))
                # Set both handles' X to the split point.
                final_right_h[i][0] = x_split
                final_left_h[i+1][0] = x_split
            else:
                # No crossover, just apply the individual clamps.
                final_right_h[i][0] = x_hr_i_clamped
                final_left_h[i+1][0] = x_hl_i1_clamped
            continue

        return final_left_h, final_right_h

    points = curve.points
    n_points = len(points)

    if (n_points < 2):
        return np.empty((0, 8), dtype=float)

    # Calculate initial handle positions
    all_left_h = [np.zeros(2) for _ in range(n_points)]
    all_right_h = [np.zeros(2) for _ in range(n_points)]

    for i in range(n_points):
        current_pt = points[i]
        prev_pt = points[i - 1] if i > 0 else None
        next_pt = points[i + 1] if i < n_points - 1 else None

        left_h, right_h = _guess_handles(current_pt, prev_pt, next_pt)
        all_left_h[i] = left_h
        all_right_h[i] = right_h
        continue

    # Apply Endpoint Handle Correction (if applicable)
    # This is a simplified version, adjust if needed for specific handle types/logic
    if (n_points > 2):
        if (points[0].handle_type == 'AUTO'):
            P0 = np.array(points[0].location, dtype=float)
            P1_orig = all_right_h[0]
            hlen = np.linalg.norm(np.subtract(P0, P1_orig)) #
            if (hlen > 1e-7):
                neighbor_handle = all_left_h[1]
                clamped_neighbor_x = max(neighbor_handle[0], P0[0])
                direction_vec = np.array([clamped_neighbor_x - P0[0], neighbor_handle[1] - P0[1]])
                nlen = np.linalg.norm(direction_vec)
                if (nlen > 1e-7):
                    scaled_direction = direction_vec * (hlen / nlen)
                    all_right_h[0] = P0 + scaled_direction

        last_idx = n_points - 1
        if (points[last_idx].handle_type == 'AUTO'):
            P3 = np.array(points[last_idx].location, dtype=float)
            P2_orig = all_left_h[last_idx]
            hlen = np.linalg.norm(np.subtract(P3, P2_orig)) #
            if (hlen > 1e-7):
                neighbor_handle = all_right_h[last_idx - 1]
                clamped_neighbor_x = min(neighbor_handle[0], P3[0])
                direction_vec = np.array([clamped_neighbor_x - P3[0], neighbor_handle[1] - P3[1]])
                nlen = np.linalg.norm(direction_vec)
                if (nlen > 1e-7):
                    scaled_direction = direction_vec * (hlen / nlen)
                    all_left_h[last_idx] = P3 + scaled_direction

    # Apply X-Monotonicity
    final_left_h, final_right_h = _points_x_monotonicity(points, all_left_h, all_right_h)

    # Build segments
    segments_list = []
    for i in range(n_points - 1):

        P0 = np.array(points[i].location, dtype=float)
        P3 = np.array(points[i + 1].location, dtype=float)

        P1 = final_right_h[i]
        P2 = final_left_h[i + 1]

        if (np.any(np.isnan(P0)) or np.any(np.isnan(P1)) or \
            np.any(np.isnan(P2)) or np.any(np.isnan(P3))):
            print(f"WARNING: NaN detected in segment {i}. Skipping.")
            continue

        segment_row = np.concatenate((P0, P1, P2, P3))
        segments_list.append(segment_row)
        continue

    if (not segments_list):
         return np.empty((0, 8), dtype=float)

    segments_array = np.array(segments_list, dtype=float)
    
    return segments_array


def is_handles_aligned(handle, anchor1, anchor2, epsilon:float=1e-6) -> bool:
    """Checks if the handle vector (anchor1 -> handle) is collinear with the
    anchor vector (anchor1 -> anchor2)."""

    V_handle = handle - anchor1
    V_anchor = anchor2 - anchor1

    # Check if handle vector has zero length (squared magnitude)
    mag_handle_sq = np.dot(V_handle, V_handle)
    if (mag_handle_sq < epsilon * epsilon):
        return True # Zero length handle is considered aligned (VECTOR)

    # Check if anchor vector has zero length (squared magnitude)
    mag_anchor_sq = np.dot(V_anchor, V_anchor)
    if (mag_anchor_sq < epsilon * epsilon):
        return False # Cannot align with a zero-length anchor segment

    # Calculate the 2D cross product's Z component
    # If vectors are A=(ax, ay) and B=(bx, by), cross_product = ax*by - ay*bx
    cross_product = (V_handle[0] * V_anchor[1]) - (V_handle[1] * V_anchor[0])

    # Return True if the cross product is close to zero (collinear)
    return (abs(cross_product) < epsilon)


def bezsegs_to_curvemapping(curve, segments:np.ndarray) -> None:
    """Apply an N x 8 NumPy array of Bézier segments to a blender curvemapping.
    Assumes `segments` is a NumPy array where each row is: [P0x, P0y, P1x, P1y, P2x, P2y, P3x, P3y]
    """

    if (not isinstance(segments, np.ndarray)):
        raise ValueError("Input segments must be a NumPy array")
    if ((segments.ndim != 2) or (segments.shape[1] != 8)):
        raise ValueError(f"Input segments array must have shape (N, 8), got {segments.shape}")

    num_segments = segments.shape[0]
    if (num_segments == 0):
        raise ValueError("Input segments array is empty")

    num_points = num_segments + 1
    reset_curvemapping(curve) # Start fresh with default 2 points

    # Ensure enough points exist in the Blender curve
    while (len(curve.points) < num_points):
        curve.points.new(0, 0) 

    # Set first point's location
    P0_first = segments[0, 0:2] # First point of first segment
    curve.points[0].location = tuple(P0_first) # Convert slice to tuple for location

    # Set subsequent points and handle types based on segments
    for i in range(num_segments):
        try:
            # Extract points directly using slicing
            P0 = segments[i, 0:2]
            P1 = segments[i, 2:4]
            P2 = segments[i, 4:6]
            P3 = segments[i, 6:8]

            # Set Point Locations
            # Location of the end point of this segment corresponds to curve.points[i+1]
            curve.points[i+1].location = tuple(P3) # Convert slice to tuple

            # vector handle types are simply aligned handles/anchors.
            # default are all auto handles. We ignore clamped handles. too similar with auto imo.
            if ((curve.points[i].handle_type == "AUTO") \
                and is_handles_aligned(P1, P0, P3)):
                curve.points[i].handle_type = "VECTOR"
            if ((curve.points[i+1].handle_type == "AUTO") \
                and is_handles_aligned(P2, P3, P0)):
                curve.points[i+1].handle_type = "VECTOR"
            continue

        except Exception as e:
            print(f"WARNING: Unexpected error processing segment {i}: {e}")
            print(f"Segment data (row): {segments[i]}")

        continue

    return None


def reset_curvemapping(curve) -> None:
    """clear all points of this curve (2 pts need to be left)"""

    points = curve.points

    while (len(curve.points)>2):
        points.remove(points[1])

    points[0].location = (0,0)
    points[1].location = (1,1)

    return None


def hash_bezsegs(segments:np.ndarray) -> str:
    """Generate a string hash value for a numpy array containing bezier curve data.
    segments (np.ndarray): An (N-1) x 8 NumPy array [P0x, P0y, P1x, P1y, P2x, P2y, P3x, P3y]."""

    if (segments is None) \
        or (not isinstance(segments, np.ndarray)) \
        or (segments.ndim != 2) \
        or (segments.shape[1] != 8):
        return None

    # Convert to bytes and hash
    return hashlib.md5(segments.tobytes()).hexdigest()


def is_bezsegs_monotonic(segments:np.ndarray, sample_rate:int=500) -> bool:
    """Check if the segments represent a curve monotonic in x.
    segments (np.ndarray): An (N) x 8 NumPy array [P0x, P0y, P1x, P1y, P2x, P2y, P3x, P3y].
    Returns True if the segments are monotonic in x, False otherwise.
    """
    points = sample_bezsegs(segments, sample_rate)
    return np.all(np.diff(points[:,0]) >= 0)


def ensure_monotonic_bezsegs(segments:np.ndarray) -> np.ndarray:
    """Ensure the segments represent a curve monotonic in x.
    This involves sorting anchor points by x-coordinate and then adjusting handles.
    Monotonicity is important for interpolation, preventing the curve from backtracking on the X axis.
    segments (np.ndarray): An (N) x 8 NumPy array [P0x, P0y, P1x, P1y, P2x, P2y, P3x, P3y].
    Returns a *new* NumPy array with the sorted and adjusted segments.
    """

    # we don't need to do anything if the curve is already monotonic
    if is_bezsegs_monotonic(segments):
        return segments

    num_segments = segments.shape[0]
    num_points = num_segments + 1

    # 1. Deconstruct into anchor points and handles
    #    anchor_handle_data format: [Ax, Ay, HLx, HLy, HRx, HRy]
    anchor_handle_data = np.zeros((num_points, 6), dtype=segments.dtype)

    # Fill Anchor locations (Ax, Ay)
    anchor_handle_data[0, 0:2] = segments[0, 0:2]  # First anchor is P0 of first segment
    anchor_handle_data[1:, 0:2] = segments[:, 6:8] # Subsequent anchors are P3 of each segment

    # Fill Left Handles (HLx, HLy)
    # First anchor's left handle defaults to its own location
    anchor_handle_data[0, 2:4] = anchor_handle_data[0, 0:2]
    # Other left handles are P2 of the preceding segment
    anchor_handle_data[1:, 2:4] = segments[:, 4:6]

    # Fill Right Handles (HRx, HRy)
    # Intermediate right handles are P1 of the current segment
    anchor_handle_data[:-1, 4:6] = segments[:, 2:4]
    # Last anchor's right handle defaults to its own location
    anchor_handle_data[-1, 4:6] = anchor_handle_data[-1, 0:2]

    # 2. Sort by Anchor X-coordinate
    sort_indices = np.argsort(anchor_handle_data[:, 0])
    sorted_anchor_handle_data = anchor_handle_data[sort_indices]

    # 3. Reconstruct segments from sorted data
    # Create a new array for the sorted segments
    sorted_segments = np.zeros((num_segments, 8), dtype=segments.dtype)

    # P0 comes from anchor i's location
    sorted_segments[:, 0:2] = sorted_anchor_handle_data[:-1, 0:2]
    # P1 comes from anchor i's right handle
    sorted_segments[:, 2:4] = sorted_anchor_handle_data[:-1, 4:6]
    # P2 comes from anchor i+1's left handle
    sorted_segments[:, 4:6] = sorted_anchor_handle_data[1:, 2:4]
    # P3 comes from anchor i+1's location
    sorted_segments[:, 6:8] = sorted_anchor_handle_data[1:, 0:2]

    # 4. Apply handle clamping to the *newly reconstructed* segments
    #    (This is the same vectorized logic as before)
    x0 = sorted_segments[:, 0]
    x1 = sorted_segments[:, 2]
    x2 = sorted_segments[:, 4]
    x3 = sorted_segments[:, 6]

    x_min = np.minimum(x0, x3)
    x_max = np.maximum(x0, x3)

    x1_clamped = np.clip(x1, x_min, x_max)
    x2_clamped = np.clip(x2, x_min, x_max)

    crossover_mask = x1_clamped > x2_clamped
    x_split = (x1_clamped + x2_clamped) / 2.0

    sorted_segments[:, 2] = np.where(crossover_mask, x_split, x1_clamped)
    sorted_segments[:, 4] = np.where(crossover_mask, x_split, x2_clamped)
    
    # 5. in rare case, we might have start/end anchors aligned with their respective handles
    # we don't want aligned handles, the lasts handles are important for curves extensions
    tolerance_align = 1e-7 # Tolerance for checking exact alignment
    epsilon_push = 1e-6     # Small amount to push away

    # Check start handle (P1 of first segment)
    # Indices: P0.x=0, P1.x=2, P3.x=6 for segment 0
    p0x_start = sorted_segments[0, 0]
    p1x_start = sorted_segments[0, 2]
    p3x_start = sorted_segments[0, 6] # Needed for push direction and clipping range
    if abs(p1x_start - p0x_start) < tolerance_align:
        # Determine push direction (towards P3)
        push_dir = np.sign(p3x_start - p0x_start)
        if push_dir == 0: push_dir = 1 # Handle zero length segment case, push right arbitrarily
        sorted_segments[0, 2] += epsilon_push * push_dir
        # Re-clip just this handle within its segment's bounds
        min_seg0_x, max_seg0_x = min(p0x_start, p3x_start), max(p0x_start, p3x_start)
        sorted_segments[0, 2] = np.clip(sorted_segments[0, 2], min_seg0_x, max_seg0_x)

    # Check end handle (P2 of last segment)
    # Indices: P0.x=0, P2.x=4, P3.x=6 for segment -1
    p0x_end = sorted_segments[-1, 0] # Needed for push direction and clipping range
    p2x_end = sorted_segments[-1, 4]
    p3x_end = sorted_segments[-1, 6]
    if abs(p2x_end - p3x_end) < tolerance_align:
            # Determine push direction (towards P0)
            push_dir = np.sign(p0x_end - p3x_end)
            if push_dir == 0: push_dir = -1 # Handle zero length segment case, push left arbitrarily
            sorted_segments[-1, 4] += epsilon_push * push_dir
            # Re-clip just this handle within its segment's bounds
            min_segN_x, max_segN_x = min(p0x_end, p3x_end), max(p0x_end, p3x_end)
            sorted_segments[-1, 4] = np.clip(sorted_segments[-1, 4], min_segN_x, max_segN_x)
             
    return sorted_segments


# def evaluate_cubic_bezseg(segment:np.ndarray, t:float) -> float:
#     """
#     Evaluate a cubic Bézier segment at parameter t.
#     evaluate segment as (np.ndarray): An (N-1) x 8 NumPy array [P0x, P0y, P1x, P1y, P2x, P2y, P3x, P3y]
#     """
#     # Ensure segment is a numpy array
#     try:
#         # Extract points
#         segment_arr = np.asarray(segment)
#         if segment_arr.shape != (8,):
#             raise ValueError(f"Expected segment shape (8,), got {segment_arr.shape}")
#         P0 = segment_arr[0:2]
#         P1 = segment_arr[2:4]
#         P2 = segment_arr[4:6]
#         P3 = segment_arr[6:8]

#     except (ValueError, TypeError) as e:
#         print(f"Error processing segment data in evaluate: {e}")
#         print(f"Segment data: {segment}")
#         return np.array([0.0, 0.0]) # Fallback

#     # Calculate point on curve
#     omt = 1.0 - t
#     omt2 = omt * omt
#     omt3 = omt2 * omt
#     t2 = t * t
#     t3 = t2 * t

#     return (P0 * omt3) + (P1 * 3.0 * omt2 * t) + (P2 * 3.0 * omt * t2) + (P3 * t3)


def sample_bezsegs(segments:np.ndarray, sampling_rate:int) -> np.ndarray:
    """Generate points from the segments numpy array using vectorized operations.
    segments (np.ndarray): An (N) x 8 NumPy array [P0x, P0y, P1x, P1y, P2x, P2y, P3x, P3y].
    sampling_rate (int): Number of steps *between* points per segment (e.g., 1 gives start/end, 2 gives start/mid/end).
    Returns a NumPy array of shape (N * sampling_rate + 1, 2) with the calculated points.
    """

    if segments is None or segments.size == 0:
        return np.empty((0, 2), dtype=segments.dtype if segments is not None else float)
    if sampling_rate < 1:
        raise ValueError("sampling_rate must be at least 1")

    num_segments = segments.shape[0]
    num_points_per_segment = sampling_rate + 1

    # Extract control points for all segments
    # Reshape to (num_segments, 4, 2) for easier access
    control_points = segments.reshape(num_segments, 4, 2)
    P0 = control_points[:, 0, :][:, np.newaxis, :] # Shape (N, 1, 2)
    P1 = control_points[:, 1, :][:, np.newaxis, :] # Shape (N, 1, 2)
    P2 = control_points[:, 2, :][:, np.newaxis, :] # Shape (N, 1, 2)
    P3 = control_points[:, 3, :][:, np.newaxis, :] # Shape (N, 1, 2)

    # Generate t values (parameterization)
    # Shape (1, num_points_per_segment, 1) to broadcast correctly with points
    t = np.linspace(0, 1, num_points_per_segment).reshape(1, num_points_per_segment, 1)

    # Calculate powers of t and (1-t)
    omt = 1.0 - t
    omt2 = omt * omt
    omt3 = omt2 * omt
    t2 = t * t
    t3 = t2 * t

    # Calculate points using the Bezier formula with broadcasting
    # Result shape: (num_segments, num_points_per_segment, 2)
    points = (P0 * omt3) + (P1 * 3.0 * omt2 * t) + (P2 * 3.0 * omt * t2) + (P3 * t3)

    # Reshape to a 2D array: (num_segments * num_points_per_segment, 2)
    all_points = points.reshape(-1, 2)

    # Remove duplicate points at segment junctions
    # Keep the first point (t=0) of the first segment.
    # Keep points from t=1/sampling_rate to t=1 for all segments.
    # Create indices to keep: 0 (start of first seg), and then 1 to sampling_rate+1 for each segment
    indices_to_keep = [0] # Keep the very first point
    for i in range(num_segments):
        start = i * num_points_per_segment + 1
        end = start + sampling_rate # +1 for num_points, -1 because index starts at 1
        indices_to_keep.extend(range(start, end + 1))
        continue

    # Ensure indices are within bounds (handles cases like sampling_rate=1 correctly)
    indices_to_keep = [idx for idx in indices_to_keep if (idx < all_points.shape[0])]
    sampled_points = all_points[indices_to_keep]

    return sampled_points


def sample_bezsegs_with_t(segments:np.ndarray, sampling_rate:int) -> tuple[list, list]:
    """Generate points and their corresponding t-values per segment using vectorized operations.
    Args:
        segments (np.ndarray): An (N) x 8 NumPy array [P0x, P0y, P1x, P1y, P2x, P2y, P3x, P3y].
        sampling_rate (int): Number of steps *between* points per segment (e.g., 1 gives start/end, 2 gives start/mid/end).
                             Results in sampling_rate + 1 points per segment.

    Returns:
        tuple[list[np.ndarray], list[np.ndarray]]:
            - points_per_segment: List where each element is a NumPy array (sampling_rate + 1, 2)
                                   containing the calculated points for one segment.
            - t_values_per_segment: List where each element is a NumPy array (sampling_rate + 1,)
                                     containing the t-values corresponding to the points in the
                                     points_per_segment list at the same index.
    """

    if (segments is None) or (segments.size == 0):
        return [], [] # Return empty lists
    if (sampling_rate < 1):
        raise ValueError("sampling_rate must be at least 1")

    num_segments = segments.shape[0]
    num_points_per_segment = sampling_rate + 1
    original_dtype = segments.dtype

    # Extract control points for all segments
    control_points = segments.reshape(num_segments, 4, 2)
    P0 = control_points[:, 0, :][:, np.newaxis, :] # Shape (N, 1, 2)
    P1 = control_points[:, 1, :][:, np.newaxis, :] # Shape (N, 1, 2)
    P2 = control_points[:, 2, :][:, np.newaxis, :] # Shape (N, 1, 2)
    P3 = control_points[:, 3, :][:, np.newaxis, :] # Shape (N, 1, 2)

    # Generate t values (parameterization)
    t_1d = np.linspace(0, 1, num_points_per_segment, dtype=np.float64) # Use float64 for precision
    # Reshape for broadcasting calculation
    t = t_1d.reshape(1, num_points_per_segment, 1)

    # Calculate powers of t and (1-t)
    omt = 1.0 - t
    omt2 = omt * omt
    omt3 = omt2 * omt
    t2 = t * t
    t3 = t2 * t

    # Calculate points using the Bezier formula with broadcasting
    # Result shape: (num_segments, num_points_per_segment, 2)
    # Ensure calculation uses float64, then potentially cast back if needed
    points = (P0.astype(np.float64) * omt3) + \
             (P1.astype(np.float64) * 3.0 * omt2 * t) + \
             (P2.astype(np.float64) * 3.0 * omt * t2) + \
             (P3.astype(np.float64) * t3)
    
    # Convert result back to original dtype if it was float32 or similar
    if (original_dtype != np.float64):
        points = points.astype(original_dtype)

    # Populate lists using list comprehensions
    # points_per_segment will be a list of (num_points_per_segment, 2) arrays
    points_per_segment = [points[i] for i in range(num_segments)]
    # t_values_per_segment will be a list of (num_points_per_segment,) arrays (all identical)
    t_values_per_segment = [t_1d for _ in range(num_segments)]

    return points_per_segment, t_values_per_segment


def casteljau_subdiv_bezsegs(segments:np.ndarray, t_map:np.ndarray, tolerance:float=1e-6) -> np.ndarray:
    """
    Batch subdivide Bézier segments at t-values.
    Args:
        segments (np.ndarray): An (N, 8) NumPy array of Bézier segments
                               [P0x, P0y, P1x, P1y, P2x, P2y, P3x, P3y].
        t_map (np.ndarray): An (N,) NumPy array of parameter values (0.0 to 1.0)
                             corresponding to each segment for subdivision. length should match segments length.
                             use 0 values for segments that should not be subdivided.
        tolerance (float): Tolerance to treat t-values near 0 or 1 as non-subdividing.
    Returns:
        np.ndarray: A new NumPy array containing all resulting segments.
    """

    # Input Validation
    if not isinstance(segments, np.ndarray) or segments.ndim != 2 or segments.shape[1] != 8:
        raise ValueError(f"Input segments must be an (N, 8) NumPy array, got shape {segments.shape}")
    num_segments = segments.shape[0]
    if not isinstance(t_map, np.ndarray) or t_map.shape != (num_segments,):
        raise ValueError(f"Input t_map must be an (N,) NumPy array, got shape {t_map.shape}")
    if num_segments == 0:
        return np.empty((0, 8), dtype=segments.dtype)

    # Perform Vectorized Calculation (same as before)
    t = np.clip(t_map, 0.0, 1.0).reshape(-1, 1)
    omt = 1.0 - t
    control_points = segments.reshape(num_segments, 4, 2)
    P0, P1, P2, P3 = control_points[:, 0, :], control_points[:, 1, :], control_points[:, 2, :], control_points[:, 3, :]
    Q0 = P0 * omt + P1 * t
    Q1 = P1 * omt + P2 * t
    Q2 = P2 * omt + P3 * t
    R0 = Q0 * omt + Q1 * t
    R1 = Q1 * omt + Q2 * t
    S = R0 * omt + R1 * t

    # Construct Potential Sub-segments
    # These arrays hold the potential results IF subdivision happens
    potential_seg1 = np.concatenate((P0, Q0, R0, S), axis=1)
    potential_seg2 = np.concatenate((S, R1, Q2, P3), axis=1)

    # Identify Segments to Subdivide
    subdivide_mask = (t_map > tolerance) & (t_map < 1.0 - tolerance) # Use original t_map for mask

    # Assemble the Output Array
    output_segments_list = []
    for i in range(num_segments):
        if subdivide_mask[i]:
            output_segments_list.append(potential_seg1[i])
            output_segments_list.append(potential_seg2[i])
        else:
            output_segments_list.append(segments[i])

    if (not output_segments_list):
        return np.empty((0, 8), dtype=segments.dtype)

    # Determine appropriate dtype (original or float if potential_seg2 was involved)
    result_dtype = np.promote_types(segments.dtype, potential_seg2.dtype)
    return np.array(output_segments_list, dtype=result_dtype)


def cut_bezsegs(segments:np.ndarray, xlocation:float, sampling_rate:int=50, tolerance:float=1e-6,) -> np.ndarray:
    """
    Subdivides Bézier segments at a given x-location by estimating the subdivision
    parameter 't' from pre-sampled points.
    Args:
        segments (np.ndarray): An (N, 8) NumPy array of Bézier segments
                               [P0x, P0y, P1x, P1y, P2x, P2y, P3x, P3y].
        xlocation (float): The target x-coordinate for subdivision.
        sampling_rate (int): The density used by sample_bezsegs_with_t to
                             generate points for estimating 't'. Higher values
                             increase accuracy but cost more computation upfront.
    Returns:
        np.ndarray: A new NumPy array containing all resulting segments after
                    subdivision. Shape will be (M, 8) where N <= M <= 2*N.
                    Returns the original array if no subdivisions occur.
    """

    if segments is None or segments.size == 0:
        return np.empty((0, 8), dtype=segments.dtype if segments is not None else float)
    if sampling_rate < 1:
        raise ValueError("sampling_rate must be at least 1")

    num_segments = segments.shape[0]

    # 1. Sample points and t-values for estimation
    try:
        points_per_segment, t_values_per_segment = sample_bezsegs_with_t(segments, sampling_rate)
    except Exception as e:
        print(f"ERROR: during sampling in cut_bezsegs: {e}")
        return segments

    if len(points_per_segment) != num_segments or len(t_values_per_segment) != num_segments:
        print(f"WARNING: Mismatch between segment count and sampling results. Returning original.")
        return segments

    # 2. Initialize the t-map for subdivision
    t_map = np.zeros(num_segments, dtype=np.float64)
    subdivide_mask = np.zeros(num_segments, dtype=bool) # Track which segments to subdivide

    # 3. Loop through segments to find estimated t-values
    for i in range(num_segments):
        P0x, P3x = segments[i, 0], segments[i, 6]

        # check if the X location is within the segment range
        if not ((P0x < xlocation < P3x) or (P3x < xlocation < P0x)):
            continue

        sampled_pts, sampled_ts = points_per_segment[i], t_values_per_segment[i]
        if ((sampled_pts.size == 0) or (sampled_ts.size == 0)):
            continue

        try:
            idx = np.argmin(np.abs(sampled_pts[:, 0] - xlocation))
            estimated_t = sampled_ts[idx]
            # Only mark for subdivision if estimated t is not too close to ends
            if (tolerance < estimated_t < (1.0 - tolerance)):
                t_map[i] = estimated_t
                subdivide_mask[i] = True
            # else: leave t_map[i] as 0.0, subdivide_mask[i] as False
        except Exception as e:
            print(f"WARNING: Error finding nearest t for segment {i}: {e}. Skipping.")

        continue

    # 4. Call the batch subdivision function
    try:
        # Use the t_map where subdivision is needed, otherwise t=0 (no split)
        subdivided_segments = casteljau_subdiv_bezsegs(segments, t_map, tolerance=tolerance)
    except Exception as e:
        print(f"ERROR: during batch subdivision in cut_bezsegs: {e}")
        return segments

    # 5. Adjust x-coordinate of the new anchor points
    # Ensure we modify a float array copy
    modified_segments = subdivided_segments.astype(float, copy=True)
    output_idx = 0
    for i in range(num_segments):
        if subdivide_mask[i]: # Check if this original segment *was* actually split
            # Adjust P3x of first child segment
            modified_segments[output_idx, 6] = xlocation
            # Adjust P0x of second child segment
            modified_segments[output_idx + 1, 0] = xlocation
            # Move output index past the two children
            output_idx += 2
        else:
            # Move output index past the single original segment
            output_idx += 1
        continue

    return modified_segments


def extend_bezsegs(segments:np.ndarray, xlocation:float, mode:str='HANDLE', tolerance:float=1e-6,):
    """
    Extends a sequence of Bézier segments to a target xlocation,
    if the xlocation is outside the current range of the segments.

    Args:
        segments (np.ndarray): An (N, 8) NumPy array of Bézier segments.
                               Assumed to be generally ordered by x for range check.
        xlocation (float): The target x-coordinate to extend to.
        mode (str): The extension mode. Must be 'HANDLE' or 'HORIZONTAL'.
        tolerance (float): Tolerance for checking if tangent x-component is near zero.

    Returns:
        np.ndarray: A new NumPy array containing the original segments plus
                    the added extension segment, if applicable. Shape will
                    be (N, 8) or (N+1, 8). Returns a copy of the original
                    if no extension is needed.
    """

    # Input Validation
    if not isinstance(segments, np.ndarray) or segments.ndim != 2 or segments.shape[1] != 8:
        raise ValueError(f"Input segments must be an (N, 8) NumPy array, got shape {segments.shape}")
    if segments.size == 0:
        print("WARNING: Input segments array is empty. Cannot extend.")
        return np.empty((0, 8), dtype=segments.dtype)

    mode = mode.upper()
    if mode not in ['HANDLE', 'HORIZONTAL']:
        raise ValueError(f"Invalid mode '{mode}'. Must be 'HANDLE' or 'HORIZONTAL'.")

    # Determine Current Range and Endpoints
    P0_orig = segments[0, 0:2].astype(float)
    P1_orig = segments[0, 2:4].astype(float)
    P2_orig = segments[-1, 4:6].astype(float)
    P3_orig = segments[-1, 6:8].astype(float)
    min_x = P0_orig[0]
    max_x = P3_orig[0]
    original_dtype = segments.dtype
    float_dtype = np.promote_types(original_dtype, float)

    # Check if Extension is Needed
    if (min_x - tolerance) <= xlocation <= (max_x + tolerance):
        return segments

    # Calculate New Segment Anchors and Handles
    new_segment_row = np.zeros(8, dtype=float_dtype)
    needs_extension = True

    if (xlocation < min_x):
        # Prepend: Extend to the left
        anchor_point = P0_orig      # Point to connect to
        connecting_handle = P1_orig # Handle defining tangent direction (P0-P1)

        P3_new = anchor_point # End of new segment is start of original

        # Calculate Y coordinate of the new start point (P0_new) based on mode
        match mode:
            case 'HORIZONTAL':
                new_y = anchor_point[1]
            case 'HANDLE':
                tangent_vec = anchor_point - connecting_handle # P0 - P1
                Tx = tangent_vec[0]
                Ty = tangent_vec[1]
                if (abs(Tx) < tolerance):
                    print("WARNING: Tangent x-component near zero when extending left. Using horizontal Y.")
                    new_y = anchor_point[1]
                else:
                    dx = xlocation - anchor_point[0] # Target x - start x (negative)
                    scale = dx / Tx
                    dy = scale * Ty
                    new_y = anchor_point[1] + dy

        P0_new = np.array([xlocation, new_y])

        # Calculate handles based on 25% interpolation
        segment_vec = P3_new - P0_new
        P1_new = P0_new + 0.25 * segment_vec
        P2_new = P3_new - 0.25 * segment_vec # = P0_new + 0.75 * segment_vec

        new_segment_row[:] = np.concatenate((P0_new, P1_new, P2_new, P3_new))
        combined_segments = np.vstack([new_segment_row, segments])

    elif (xlocation > max_x):
        # Append: Extend to the right
        anchor_point = P3_orig      # Point to connect to
        connecting_handle = P2_orig # Handle defining tangent direction (P3-P2)

        P0_new = anchor_point # Start of new segment is end of original

        # Calculate Y coordinate of the new end point (P3_new) based on mode
        match mode:
            case 'HORIZONTAL':
                new_y = anchor_point[1]
            case 'HANDLE':
                tangent_vec = anchor_point - connecting_handle # P3 - P2
                Tx = tangent_vec[0]
                Ty = tangent_vec[1]
                if (abs(Tx) < tolerance):
                    print("WARNING: Tangent x-component near zero when extending right. Using horizontal Y.")
                    new_y = anchor_point[1]
                else:
                    dx = xlocation - anchor_point[0] # Target x - start x (positive)
                    scale = dx / Tx
                    dy = scale * Ty
                    new_y = anchor_point[1] + dy

        P3_new = np.array([xlocation, new_y])

        # Calculate handles based on 25% interpolation
        segment_vec = P3_new - P0_new
        P1_new = P0_new + 0.25 * segment_vec
        P2_new = P3_new - 0.25 * segment_vec # = P0_new + 0.75 * segment_vec

        new_segment_row[:] = np.concatenate((P0_new, P1_new, P2_new, P3_new))
        combined_segments = np.vstack([segments, new_segment_row])

    else:
         needs_extension = False
         combined_segments = segments.copy()

    # Ensure final array has a compatible dtype
    if needs_extension:
        final_dtype = np.promote_types(original_dtype, float_dtype)
        return combined_segments.astype(final_dtype, copy=False)
    else:
        return combined_segments.astype(original_dtype, copy=False)


# def mirror_bezsegs(segments: np.ndarray):
#     """
#     Mirrors Bézier segments horizontally across the y-axis (x=0).

#     Args:
#         segments (np.ndarray): An (N, 8) NumPy array of Bézier segments
#                                [P0x, P0y, P1x, P1y, P2x, P2y, P3x, P3y].

#     Returns:
#         np.ndarray: A new (N, 8) NumPy array containing the mirrored segments.
#                     The order of the points within each segment (P0..P3) is
#                     maintained, only their x-coordinates are negated.
#     """
#     # Input Validation
#     if not isinstance(segments, np.ndarray) or segments.ndim != 2 or segments.shape[1] != 8:
#         raise ValueError(f"Input segments must be an (N, 8) NumPy array, got shape {segments.shape}")
#     if segments.size == 0:
#         return np.empty((0, 8), dtype=segments.dtype)

#     # Create a float copy for modification
#     # This prevents modifying the original and handles potential integer inputs
#     mirrored_segments = segments.astype(float, copy=True)

#     # Negate all X coordinates
#     # X coordinates are at columns 0, 2, 4, 6
#     mirrored_segments[:, 0] *= -1.0 # P0x
#     mirrored_segments[:, 2] *= -1.0 # P1x
#     mirrored_segments[:, 4] *= -1.0 # P2x
#     mirrored_segments[:, 6] *= -1.0 # P3x

#     # Y coordinates (columns 1, 3, 5, 7) remain unchanged

#     # Return mirrored segments (cast back if original was not float?)
#     # Usually returning float is fine, but we can try to preserve original type if needed
#     try:
#         # Attempt to cast back to original type if it makes sense (e.g., if original was int)
#         # Note: This might lose precision if the original was int and negation created non-ints
#         # For geometric operations, float is usually preferred anyway.
#         if np.can_cast(mirrored_segments, segments.dtype, casting='same_kind'):
#              return mirrored_segments.astype(segments.dtype, copy=False)
#         else:
#              return mirrored_segments # Return as float if casting back is unsafe/lossy
#     except:
#         # Fallback to returning the float array
#          return mirrored_segments


def match_bezsegs(segsA:np.ndarray, segsB:np.ndarray, cut_precision:int=50, tolerance:float=1e-6,):
    """
    Matches two Bézier curve segment arrays to have the same x-range and aligned anchors.
    Args:
        segsA (np.ndarray): First curve as an (N, 8) NumPy array.
        segsB (np.ndarray): Second curve as an (M, 8) NumPy array.
        cut_precision (int): Sampling rate used by cut_bezsegs for 't' estimation.
        tolerance (float): Tolerance for floating point comparisons.
    Returns:
        tuple[np.ndarray, np.ndarray]: The matched segment arrays (matched_A, matched_B).
                                       Shapes will likely differ from input due to subdivisions.
    """

    # Handle Empty Inputs
    if (segsA is None) or (segsA.size == 0):
        print("WARNING: match_bezsegs(): segsA is empty.")
        return None
    if (segsB is None) or (segsB.size == 0):
        print("WARNING: match_bezsegs(): segsB is empty.")
        return None

    # Ensure Float for Calculations
    segsA = segsA.astype(float)
    segsB = segsB.astype(float)

    # 1. Find Global X-Range
    min_xA = segsA[0, 0]
    max_xA = segsA[-1, 6]
    min_xB = segsB[0, 0]
    max_xB = segsB[-1, 6]

    global_min_x = min(min_xA, min_xB)
    global_max_x = max(max_xA, max_xB)

    # 2. Extend Curves
    try:
        # Extend A Start
        if (min_xA > (global_min_x+tolerance)): segsA = extend_bezsegs(segsA, global_min_x, 'HANDLE', tolerance)
        # Extend A End
        if (max_xA < (global_max_x-tolerance)): segsA = extend_bezsegs(segsA, global_max_x, 'HANDLE', tolerance)
        # Extend B Start
        if (min_xB > (global_min_x+tolerance)): segsB = extend_bezsegs(segsB, global_min_x, 'HANDLE', tolerance)
        # Extend B End
        if (max_xB < (global_max_x-tolerance)): segsB = extend_bezsegs(segsB, global_max_x, 'HANDLE', tolerance)
    except Exception as e:
        print(f"ERROR: during curve extension: {e}. Returning potentially unextended curves.")
        # Return current state before subdivision attempt
        return segsA, segsB

    # 3. Collect All Knot X-Coordinates
    knots_A_x = np.concatenate(([segsA[0, 0]], segsA[:, 6]))
    knots_B_x = np.concatenate(([segsB[0, 0]], segsB[:, 6]))
    all_knots_x = np.concatenate((knots_A_x, knots_B_x))

    # 4 & 5. Iterative Subdivision
    for x_knot in all_knots_x:
        # Skip subdividing exactly at the global boundaries
        if abs(x_knot - global_min_x) < tolerance or abs(x_knot - global_max_x) < tolerance:
            continue
        try:
            # Subdivide A at this x-location
            segsA = cut_bezsegs(segsA, x_knot, cut_precision)
            # Subdivide B at this x-location
            segsB = cut_bezsegs(segsB, x_knot, cut_precision)

        except Exception as e:
            print(f"ERROR: during subdivision at x={x_knot}: {e}. Stopping subdivision process.")
            # Return the segments as they were before the error
            return segsA, segsB

        continue

    # NOTE known issue
    # if the curve has two anchors at the same X location, we fail to match them.
    if (segsA.shape[0] != segsB.shape[0]):
        print(f"ERROR: match_bezsegs failed to return arrays of the same length. Cannot mix. len {segsA.shape[0]} != {segsB.shape[0]}")
        print("Are some of your knots on the exact same X location? we need to handle that case yet..")
        print("X locations A:", segsA[:, [0,6]])
        print("X locations B:", segsB[:, [0,6]])
        print("")
        return None

    return segsA, segsB


def match_bounds(segsMod:np.ndarray, segsRef:np.ndarray, rescale_x:bool=True, rescale_y:bool=False, tolerance:float=1e-6):
    """
    Transforms (translates and scales) segsMod so its overall start and end points match those of segsRef.
    Applies independent scaling and translation to X and Y coordinates.
    Args:
        segsMod (np.ndarray): Curve segments to transform (B). (M, 8) array.
        segsRef (np.ndarray): Curve segments defining target bounds (A). (N, 8) array.
        tolerance (float): Tolerance for checking zero span.
        rescale_x, rescale_y (bool): Whether to rescale the X and Y coordinates.
    Returns:
        np.ndarray: The transformed segsMod array (M, 8) with bounds matching
                    segsRef. Returns a copy of the input if modification
                    is not possible (e.g., empty input, zero span).
    """
    if (segsMod is None) or (segsMod.size==0):
        print("ERROR: match_bounds(segsMod) is empty in match_bounds.")
        return None
    if (segsRef is None) or (segsRef.size==0):
        print("ERROR: match_bounds(segsRef) is empty in match_bounds. Cannot match.")
        return None

    # Extract Bounds
    P0A = segsRef[0, 0:2].astype(float)
    P3A = segsRef[-1, 6:8].astype(float)
    P0B = segsMod[0, 0:2].astype(float)
    P3B = segsMod[-1, 6:8].astype(float)

    # Calculate Spans
    spanXA = abs(P3A[0] - P0A[0])
    spanYA = abs(P3A[1] - P0A[1])
    spanXB = abs(P3B[0] - P0B[0])
    spanYB = abs(P3B[1] - P0B[1])

    # Calculate Scale Factors
    scale_x = 1.0
    if (spanXB > tolerance):
        scale_x = spanXA / spanXB
    elif (spanXA > tolerance):
        # NOTE how do we handle case where start/end of B are at the same X location?
        scale_x = 1.0

    scale_y = 1.0
    if (spanYB > tolerance):
        scale_y = spanYA / spanYB
    elif (spanYA > tolerance):
        # NOTE how do we handle case where start/end of B are at the same Y location?
        scale_y = 1.0

    # Apply Transformation..
    
    # ensure our array is of floats
    segsMod = segsMod.astype(float)

    # Reshape to access points easily: (num_segments * 4, 2)
    num_b_segments = segsMod.shape[0]
    points_b = segsMod.reshape(-1, 2) # Reshapes to (N*4, 2)

    # Translate B so P0B is at origin
    points_b -= P0B

    # Rescaling
    if (rescale_x): points_b[:, 0] *= abs(scale_x) # Scale x coordinates
    if (rescale_y): points_b[:, 1] *= abs(scale_y) # Scale y coordinates

    # Translate B so the (now scaled) P0B' lands on P0A
    points_b += P0A

    # Reshape back to (N, 8)
    segsMod = points_b.reshape(num_b_segments, 8)

    # Ensure final array has a compatible dtype with original
    dtype = np.promote_types(segsMod.dtype, float)
    segsMod = segsMod.astype(dtype,)
    
    return segsMod


def lerp_bezsegs(segsA:np.ndarray, segsB:np.ndarray, mixfac:float, cut_precision:int=50, tolerance:float=1e-6):
    """
    Mixes (interpolates) between two Bézier curve segment arrays.
    If the number of segments differs, new segments will be added at similar X locations.
    Args:
        segsA (np.ndarray): First curve as an (N, 8) NumPy array.
        segsB (np.ndarray): Second curve as an (M, 8) NumPy array.
        mixfac (float): The mixing factor (0.0 returns segsA, 1.0 returns segsB).
        extend_mode (str): Mode used by match_bezsegs if alignment is needed.
                           Defaults to 'HORIZONTAL'.
        cut_precision (int): Sampling rate used by match_bezsegs if alignment is needed.
                                 Defaults to 50.
        tolerance (float): Tolerance for comparing mixfac to 0 and 1, and used internally
                     by match_bezsegs.
    Returns:
        np.ndarray: The resulting mixed Bézier curve as an (L, 8) NumPy array.
                    L will be the length of segsA/segsB after potential matching.
    """

    # Clamp mixfac just in case it's slightly outside [0, 1] after tolerance check
    mixfac = np.clip(mixfac, 0.0, 1.0)

    # Ensure Curves have the same numbers of segments, subdivide in place if needed
    if (segsA.shape[0] != segsB.shape[0]):
        try:
            # we move B to segs A in order to match A start/end bounds
            newsB = match_bounds(segsB, segsA, rescale_x=True, rescale_y=False)
            # Call match_bezsegs to get aligned versions
            segsA, newsB = match_bezsegs(segsA, newsB, cut_precision=cut_precision, tolerance=tolerance,)
            # Verify matching worked (should have same length now)
            if (segsA.shape[0] != newsB.shape[0]):
                 print(f"ERROR: internal match_bezsegs() failed to return segments of same knots length. Cannot mix. len{segsA.shape[0]} with len{newsB.shape[0]}")
                 return None
            # move b back to it's original position after the subdivision
            segsB = match_bounds(newsB, segsB, rescale_x=True, rescale_y=False)

        except Exception as e:
            print(f"ERROR: during match_bezsegs in lerp_bezsegs: {e}.")
            return None

    # Handle Edge Cases for mixfac
    if (abs(mixfac - 0.0) < tolerance):
        return segsA
    if (abs(mixfac - 1.0) < tolerance):
        return segsB

    # Check for empty arrays after potential matching
    if (segsA.size == 0) or (segsB.size == 0):
         print("WARNING: One or both segment arrays are empty after matching. Returning empty.")
         return None

    # Perform Optimized NumPy Lerp
    try:
        # Linear interpolation: result = A * (1 - factor) + B * factor. Ensure float.
        mixed_segments = segsA.astype(float) * (1.0 - mixfac) + segsB.astype(float) * mixfac
    except Exception as e:
        print(f"ERROR: during segment interpolation: {e}.")
        return None

    return mixed_segments


def looped_offset_bezsegs(segments: np.ndarray, offset: float, cut_precision:int=100, tolerance:float=1e-6) -> np.ndarray:
    """
    Offsets a monotonic Bézier curve segment array horizontally, wrapping the curve
    around its original x-range.

    Args:
        segments (np.ndarray): The Bézier curve segments to offset. Expected to
                               be monotonic on the X axis. (N, 8) array.
        offset (float): The amount to offset the curve horizontally. Positive shifts
                        right, negative shifts left.
        cut_precision (int): The sampling rate precision used by cut_bezsegs.
        tolerance (float): Tolerance for float comparisons and cutting.

    Returns:
        np.ndarray: The looped and offset Bézier curve segments. Shape might
                    differ from input due to cutting. Returns None on error or
                    if segments are invalid.
    """

    # ensure our segments are monotonic
    mono_segments = ensure_monotonic_bezsegs(segments)

    # if offset is 0.0, we don't need to loop or cut anything
    if offset == 0.0:
        return mono_segments

    # --- Calculate Range and Effective Offset ---
    start_xloc = mono_segments[0, 0]
    end_xloc = mono_segments[-1, 6]
    distance = end_xloc - start_xloc

    if distance <= tolerance:
        print("Warning: Curve has zero or negligible width. Cannot loop.")
        return mono_segments # Return the monotonic version

    # Calculate the effective offset within the curve's width
    # fmod is generally better for float modulo
    effective_offset = np.fmod(offset, distance)

    # Determine the location where the cut needs to happen in the *original* monotonic curve
    cut_location = start_xloc + effective_offset
    # Adjust cut location if negative offset wrapped around
    if cut_location < start_xloc:
        cut_location += distance
    elif cut_location >= end_xloc: # Should ideally not happen due to fmod, but safety
        cut_location -= distance

    # 1. Cut the original monotonic curve
    cut_segments = cut_bezsegs(mono_segments, cut_location, cut_precision, tolerance)

    # 2. Find the cutted segments
    split_idx = None
    for i in range(cut_segments.shape[0]):
        # Check if the end point of segment i is the cut location
        if (abs(cut_segments[i, 6] - cut_location) <= tolerance):
            split_idx = i + 1
            break
        # Also check if start point of segment i is the cut (if cut landed on knot)
        if (abs(cut_segments[i, 0] - cut_location) <= tolerance and (i > 0)):
             split_idx = i
             break
    # 2.5 if no cut found, it means the segment was not cut, and we use an existing segment
    if (split_idx is None):
        # TODO
        # here, if the split_idx is none, it means the segment was not cut (likely at an existing knot)
        # so we need to find the segments which anchor end or start matches the cut location, depending on the offset direction
        return None

    # 3. Move the cutted segments to start/end
    part1 = cut_segments[:split_idx].astype(float, copy=True) # Part before cut
    part2 = cut_segments[split_idx:].astype(float, copy=True) # Part after cut

    # Create translation vector (only affects X)
    if effective_offset > 0:
        # Part 1 (before cut) moves to the end, shifted right by distance
        part1[:, 0] += distance # P0x
        part1[:, 2] += distance # P1x
        part1[:, 4] += distance # P2x
        part1[:, 6] += distance # P3x
        # Combine: part2 followed by translated part1
        final_segments = np.vstack([part2, part1])

    else: # effective_offset < 0
        # Part 2 (after cut) moves to the beginning, shifted left by distance
        part2[:, 0] -= distance # P0x
        part2[:, 2] -= distance # P1x
        part2[:, 4] -= distance # P2x
        part2[:, 6] -= distance # P3x
        # Combine: translated part2 followed by part1
        final_segments = np.vstack([part2, part1])

    # 4. Ensure original Start location  ---
    new_start  = final_segments[0, 0]
    distance = new_start - start_xloc
    final_segments[:, 0] -= distance # P0x
    final_segments[:, 2] -= distance # P1x
    final_segments[:, 4] -= distance # P2x
    final_segments[:, 6] -= distance # P3x

    return final_segments