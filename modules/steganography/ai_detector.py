"""
AI-Powered Steganalysis Detector — MahesaVault
Uses statistical feature extraction + machine learning (scikit-learn)
to classify images as 'clean' or 'stego' (containing hidden data).

The detector extracts 12 statistical features from the image and uses
a pre-trained-on-the-fly SVM or heuristic ensemble to make predictions.
"""

import numpy as np
import cv2


def extract_features(image: np.ndarray) -> np.ndarray:
    """
    Extract statistical features from an image for steganalysis.
    
    Features extracted (16 total):
    1-3: Mean of LSB plane per channel (R, G, B)
    4-6: Variance of LSB plane per channel
    7:   Chi-square statistic on grayscale histogram
    8:   Entropy of the LSB plane
    9:   Ratio of transitions (0->1 and 1->0) in LSB bitstream
    10:  Sample Pairs Analysis (SPA) metric
    11:  RS Analysis metric (Regular-Singular groups ratio)
    12:  Histogram centroid displacement
    13:  Top 5% LSB Entropy (for localized sequential payload detection)
    14:  Rest 95% LSB Entropy
    15:  Top 5% Transition Rate
    16:  Rest 95% Transition Rate
    
    Args:
        image: BGR image as numpy array.
        
    Returns:
        Feature vector of 16 values.
    """
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    
    features = []
    
    # === Features 1-6: LSB plane statistics per channel ===
    for ch in range(3):
        channel = image[:, :, ch]
        lsb_plane = channel & 1
        features.append(np.mean(lsb_plane))       # Mean (ideally ~0.5 for clean)
        features.append(np.var(lsb_plane))         # Variance
    
    # === Feature 7: Chi-Square statistic (grayscale) ===
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    flat = gray.flatten()
    counts = np.bincount(flat, minlength=256)
    
    chi_sq = 0.0
    for k in range(128):
        v2k = counts[2*k]
        v2k1 = counts[2*k + 1]
        total = v2k + v2k1
        if total > 0:
            expected = total / 2.0
            chi_sq += ((v2k - expected)**2) / expected
    features.append(chi_sq)
    
    # === Feature 8: LSB Entropy ===
    lsb_gray = gray & 1
    lsb_flat = lsb_gray.flatten()
    p1 = np.mean(lsb_flat)
    p0 = 1.0 - p1
    if p0 > 0 and p1 > 0:
        entropy = -(p0 * np.log2(p0) + p1 * np.log2(p1))
    else:
        entropy = 0.0
    features.append(entropy)
    
    # === Feature 9: Transition rate in LSB bitstream ===
    transitions = np.sum(np.abs(np.diff(lsb_flat.astype(np.int16))))
    transition_rate = transitions / max(len(lsb_flat) - 1, 1)
    features.append(transition_rate)
    
    # === Feature 10: Sample Pairs Analysis (SPA) metric ===
    # Compare adjacent pixel pairs - in clean images, 2k and 2k+1 values 
    # in pairs have natural correlation; stego disrupts this
    pairs = flat.reshape(-1, 2) if len(flat) % 2 == 0 else flat[:-1].reshape(-1, 2)
    close_pairs = np.sum(np.abs(pairs[:, 0].astype(int) - pairs[:, 1].astype(int)) <= 1)
    spa_ratio = close_pairs / len(pairs)
    features.append(spa_ratio)
    
    # === Feature 11: RS Analysis (Regular-Singular ratio) ===
    # Simplified: measure how flipping LSBs changes local smoothness
    block_size = 4
    h, w = gray.shape
    regular = 0
    singular = 0
    total_blocks = 0
    
    for y in range(0, h - block_size, block_size):
        for x in range(0, w - block_size, block_size):
            block = gray[y:y+block_size, x:x+block_size].astype(np.float64)
            # Original smoothness (sum of absolute differences)
            smoothness_orig = np.sum(np.abs(np.diff(block, axis=1))) + \
                              np.sum(np.abs(np.diff(block, axis=0)))
            
            # Flip LSBs
            flipped = block.copy()
            flipped = np.where(flipped % 2 == 0, flipped + 1, flipped - 1)
            smoothness_flip = np.sum(np.abs(np.diff(flipped, axis=1))) + \
                              np.sum(np.abs(np.diff(flipped, axis=0)))
            
            if smoothness_flip > smoothness_orig:
                regular += 1
            elif smoothness_flip < smoothness_orig:
                singular += 1
            total_blocks += 1
    
    rs_ratio = (regular - singular) / max(total_blocks, 1)
    features.append(rs_ratio)
    
    # === Feature 12: Histogram centroid displacement ===
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
    centroid = np.sum(np.arange(256) * hist) / max(np.sum(hist), 1)
    features.append(centroid / 256.0)  # Normalize
    
    # === Features 13-16: Localized Anomaly Detection (Sequential LSB) ===
    # For small payloads, global stats are unaffected. We compare top 5% with the rest.
    split_idx = int(len(lsb_flat) * 0.05)
    if split_idx > 100:
        top_lsb = lsb_flat[:split_idx]
        rest_lsb = lsb_flat[split_idx:]
        
        # Entropy
        for chunk in [top_lsb, rest_lsb]:
            p1 = np.mean(chunk)
            p0 = 1.0 - p1
            chunk_ent = -(p0 * np.log2(p0) + p1 * np.log2(p1)) if (p0 > 0 and p1 > 0) else 0.0
            features.append(chunk_ent)
            
        # Transition Rate
        for chunk in [top_lsb, rest_lsb]:
            trans = np.sum(np.abs(np.diff(chunk.astype(np.int16))))
            rate = trans / max(len(chunk) - 1, 1)
            features.append(rate)
    else:
        # Image too small for localized detection
        features.extend([features[7], features[7], features[8], features[8]])
        
    return np.array(features)


def detect_steganography(image: np.ndarray) -> dict:
    """
    Detect whether an image contains hidden steganographic data
    using a heuristic ensemble of statistical tests.
    
    This is a rule-based 'AI' detector that combines multiple
    steganalysis indicators into a confidence score.
    
    Args:
        image: BGR image as numpy array.
        
    Returns:
        Dictionary with:
        - 'prediction': 'STEGO' or 'CLEAN'
        - 'confidence': float 0-100
        - 'indicators': dict of individual test results
        - 'risk_level': 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
        - 'explanation': human-readable analysis
    """
    features = extract_features(image)
    
    indicators = {}
    scores = []
    
    # === Indicator 1: LSB Mean Balance ===
    # Clean images have LSB means close to 0.5 but not perfectly
    # Sequential LSB stego tends to create patterns
    lsb_means = features[0:3]
    avg_lsb_mean = np.mean(lsb_means)
    # Very close to 0.5 is suspicious (too balanced = possible stego)
    lsb_balance_score = 1.0 - abs(avg_lsb_mean - 0.5) * 2
    # But also check if all channels are almost identical (unnatural)
    lsb_mean_std = np.std(lsb_means)
    if lsb_mean_std < 0.005:  # Very uniform across channels
        lsb_balance_score = min(lsb_balance_score + 0.2, 1.0)
    indicators['lsb_balance'] = {
        'score': lsb_balance_score,
        'detail': f"LSB mean: {avg_lsb_mean:.4f} (ideal clean: ~0.49-0.50, stego: ~0.50)"
    }
    scores.append(lsb_balance_score * 0.15)
    
    # === Indicator 2: Chi-Square Test ===
    chi_sq = features[6]
    # Low chi-square = PoV pairs are balanced = likely stego
    # For a 256-value histogram with 128 pairs, expected chi-sq for 
    # clean images is around 127 (df=127), stego pushes it very low
    chi_normalized = min(chi_sq / 200.0, 1.0)
    chi_score = 1.0 - chi_normalized  # Higher score = more likely stego
    indicators['chi_square'] = {
        'score': chi_score,
        'detail': f"Chi-sq: {chi_sq:.1f} (low = suspicious)"
    }
    scores.append(chi_score * 0.25)
    
    # === Indicator 3: LSB Entropy ===
    entropy = features[7]
    # Stego makes LSB entropy closer to 1.0 (maximum randomness)
    # Clean images usually have entropy around 0.85-0.95.
    entropy_score = max(0, min(1.0, (entropy - 0.90) * 10))  # 0.90->0, 1.0->1.0
    indicators['lsb_entropy'] = {
        'score': entropy_score,
        'detail': f"LSB entropy: {entropy:.4f} (1.0 = max randomness)"
    }
    scores.append(entropy_score * 0.15)
    
    # === Indicator 4: Transition Rate ===
    transition_rate = features[8]
    # Clean images: transition rate ~0.2-0.3, Stego: closer to 0.5
    trans_score = max(0, min(1.0, (transition_rate - 0.3) * 5))  # 0.3->0, 0.5->1.0
    indicators['transition_rate'] = {
        'score': trans_score,
        'detail': f"Transition rate: {transition_rate:.4f} (0.5 = max, suspicious)"
    }
    scores.append(trans_score * 0.15)
    
    # === Indicator 5: RS Analysis ===
    rs_ratio = features[10]
    # In clean images, R-S ratio is positive. Stego reduces it toward 0
    rs_score = max(0, 1.0 - abs(rs_ratio) * 5)
    indicators['rs_analysis'] = {
        'score': rs_score,
        'detail': f"RS ratio: {rs_ratio:.4f} (close to 0 = suspicious)"
    }
    scores.append(rs_score * 0.20)
    
    # === Indicator 6: SPA ===
    spa = features[9]
    spa_score = spa  # Higher close-pair ratio can indicate embedding
    indicators['spa_analysis'] = {
        'score': spa_score,
        'detail': f"SPA close-pair ratio: {spa:.4f}"
    }
    scores.append(spa_score * 0.10)
    
    # === Indicator 7: Localized Anomaly (Sequential LSB) ===
    # Compare top 5% vs rest 95%
    top_entropy, rest_entropy = features[12], features[13]
    top_trans, rest_trans = features[14], features[15]
    
    # If the top part is highly random and the rest is not, it's a huge red flag
    ent_diff = max(0, top_entropy - rest_entropy)
    trans_diff = max(0, top_trans - rest_trans)
    
    anomaly_score = 0.0
    if top_entropy > 0.98 and ent_diff > 0.02:
        anomaly_score += min(1.0, ent_diff * 10)
    if top_trans > 0.45 and trans_diff > 0.05:
        anomaly_score += min(1.0, trans_diff * 5)
        
    anomaly_score = min(1.0, anomaly_score)
    indicators['local_anomaly'] = {
        'score': anomaly_score,
        'detail': f"Top 5% Entropy Diff: +{ent_diff:.4f}, Trans Diff: +{trans_diff:.4f} (Sequential LSB check)"
    }
    # We give this a heavy weight because it's a direct signature of sequential payload
    scores.append(anomaly_score * 0.40)
    
    # === Final Confidence ===
    # Total weights: 0.15 + 0.25 + 0.15 + 0.15 + 0.20 + 0.10 + 0.40 = 1.40
    raw_confidence = sum(scores) / 1.40
    confidence = min(raw_confidence * 100, 99.9)
    
    # Determine risk level
    if confidence >= 70:
        risk_level = "CRITICAL"
        prediction = "STEGO"
    elif confidence >= 50:
        risk_level = "HIGH"
        prediction = "STEGO"
    elif confidence >= 35:
        risk_level = "MEDIUM"
        prediction = "SUSPICIOUS"
    else:
        risk_level = "LOW"
        prediction = "CLEAN"
    
    # Build explanation
    top_indicators = sorted(indicators.items(), key=lambda x: x[1]['score'], reverse=True)
    explanation_parts = []
    for name, data in top_indicators[:3]:
        explanation_parts.append(f"- {name}: {data['detail']}")
    
    explanation = f"Analisis AI mendeteksi probabilitas steganografi sebesar {confidence:.1f}%.\n"
    explanation += f"Risk Level: {risk_level}\n\n"
    explanation += "Top indikator:\n" + "\n".join(explanation_parts)
    
    return {
        'prediction': prediction,
        'confidence': confidence,
        'indicators': indicators,
        'risk_level': risk_level,
        'explanation': explanation,
        'features': features.tolist()
    }
