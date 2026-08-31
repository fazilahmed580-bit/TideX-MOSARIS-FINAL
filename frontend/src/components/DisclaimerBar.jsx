import React from 'react';
import { AlertTriangle } from 'lucide-react';

export default function DisclaimerBar() {
  return (
    <div className="disclaimer-bar-light">
      <AlertTriangle size={18} style={{ flexShrink: 0, color: '#d97706' }} />
      <div>
        <strong>INVESTIGATION PRIORITY DISCLAIMER:</strong> Attribution scores represent multi-factor investigation prioritization only and are NOT a probability of guilt, legal finding, or proof of legal responsibility.
      </div>
    </div>
  );
}
