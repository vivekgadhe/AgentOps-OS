import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Ban, Check, XCircle } from 'lucide-react';

import { Button } from '../../components/ui/Button';
import { getApiErrorMessage } from '../../lib/api-error';
import { approvalsApi } from '../dashboard/dashboard.api';
import type { ApprovalItem } from '../dashboard/dashboard.types';

export function ApprovalActions({
  approval,
  currentUserId,
  role,
  onComplete,
}: {
  approval: ApprovalItem;
  currentUserId: string;
  role: string;
  onComplete: () => void;
}) {
  const queryClient = useQueryClient();
  const [reason, setReason] = useState('');
  const [error, setError] = useState<string | null>(null);
  const isPending = approval.status === 'pending';
  const canDecide = role === 'admin' && approval.requester_user_id !== currentUserId;
  const canCancel = role === 'admin' || approval.requester_user_id === currentUserId;
  const mutation = useMutation({
    mutationFn: async (action: 'approve' | 'reject' | 'cancel') => {
      if (action === 'approve') return approvalsApi.approve(approval.id, reason);
      if (action === 'reject') return approvalsApi.reject(approval.id, reason);
      return approvalsApi.cancel(approval.id);
    },
    onSuccess: async () => {
      setError(null);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['approvals'] }),
        queryClient.invalidateQueries({ queryKey: ['approval', approval.id] }),
        queryClient.invalidateQueries({ queryKey: ['workflow', approval.workflow_run_id] }),
        queryClient.invalidateQueries({ queryKey: ['dashboard'] }),
      ]);
      onComplete();
    },
    onError: (cause) => setError(getApiErrorMessage(cause, 'Unable to update this approval request.')),
  });

  if (!isPending) return <div className="phase2-muted">This approval request has already been decided: {approval.status}.</div>;

  return (
    <div className="phase2-approval-actions">
      {canDecide && <label className="phase2-field">Decision reason (optional)<textarea rows={2} maxLength={2000} value={reason} onChange={(event) => setReason(event.target.value)} placeholder="Add context for the audit record…" /></label>}
      {!canDecide && <div className="phase2-alert warning">{role !== 'admin' ? 'Only an administrator can approve or reject this request.' : 'The requester cannot approve their own action.'}</div>}
      {error && <div className="phase2-alert error">{error}</div>}
      <div className="phase2-heading-actions approval-action-buttons">
        {canDecide && <>
          <Button className="phase2-approve-button" disabled={mutation.isPending} onClick={() => mutation.mutate('approve')}><Check size={15} /> Approve</Button>
          <Button variant="secondary" className="phase2-reject-button" disabled={mutation.isPending} onClick={() => mutation.mutate('reject')}><XCircle size={15} /> Reject</Button>
        </>}
        {canCancel && <Button variant="ghost" disabled={mutation.isPending} onClick={() => mutation.mutate('cancel')}><Ban size={15} /> Cancel request</Button>}
      </div>
    </div>
  );
}
