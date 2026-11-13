defmodule Eria.Governance do
  @moduledoc """
  Records independent review and scoped authorization decisions.

  This module validates declared separation of roles and records an external
  approval reference. It does not authenticate identities, verify signatures,
  or execute actions. Research-only diagnostic support remains non-actuating.
  """

  def record_review(attrs) when is_map(attrs) do
    submitter = Map.get(attrs, :submitter_id)
    reviewer = Map.get(attrs, :reviewer_id)
    decision = Map.get(attrs, :decision)
    scope = Map.get(attrs, :scope)
    evidence_ids = Map.get(attrs, :evidence_ids)
    reviewed_at = Map.get(attrs, :reviewed_at)

    cond do
      not nonempty?(submitter) -> {:error, :submitter_required}
      not nonempty?(reviewer) -> {:error, :reviewer_required}
      submitter == reviewer -> {:error, :reviewer_must_be_independent}
      decision not in [:approved, :rejected, :needs_revision] -> {:error, :invalid_review_decision}
      not nonempty?(scope) -> {:error, :review_scope_required}
      not (is_list(evidence_ids) and evidence_ids != []) -> {:error, :review_evidence_required}
      not valid_datetime?(reviewed_at) -> {:error, :invalid_review_timestamp}
      true ->
        {:ok, %{
          id: Map.get(attrs, :id) || new_id("review"),
          submitter_id: submitter,
          reviewer_id: reviewer,
          decision: decision,
          scope: scope,
          evidence_ids: evidence_ids,
          reviewed_at: reviewed_at,
          identity_verification: :external_requirement
        }}
    end
  end

  def record_authorization(attrs) when is_map(attrs) do
    review = Map.get(attrs, :review)
    requester = Map.get(attrs, :requester_id)
    authorizer = Map.get(attrs, :authorizer_id)
    action = Map.get(attrs, :action)
    target = Map.get(attrs, :target)
    scope = Map.get(attrs, :scope)
    expires_at = Map.get(attrs, :expires_at)
    approval_reference = Map.get(attrs, :approval_reference)

    cond do
      not is_map(review) -> {:error, :independent_review_required}
      Map.get(review, :decision) != :approved -> {:error, :approved_review_required}
      not nonempty?(requester) -> {:error, :requester_required}
      not nonempty?(authorizer) -> {:error, :authorizer_required}
      authorizer in [requester, Map.get(review, :submitter_id), Map.get(review, :reviewer_id)] ->
        {:error, :authorizer_must_be_independent}
      not nonempty?(action) -> {:error, :action_required}
      not nonempty?(target) -> {:error, :target_required}
      not nonempty?(scope) or scope != Map.get(review, :scope) -> {:error, :authorization_scope_mismatch}
      not valid_datetime?(expires_at) -> {:error, :invalid_expiry}
      not nonempty?(approval_reference) -> {:error, :explicit_approval_reference_required}
      true ->
        {:ok, %{
          id: Map.get(attrs, :id) || new_id("authorization"),
          requester_id: requester,
          authorizer_id: authorizer,
          review_id: Map.get(review, :id),
          action: action,
          target: target,
          scope: scope,
          expires_at: expires_at,
          approval_reference: approval_reference,
          status: :recorded_not_cryptographically_verified,
          execution_enabled: false
        }}
    end
  end

  def record_review(_), do: {:error, :invalid_review_attributes}
  def record_authorization(_), do: {:error, :invalid_authorization_attributes}

  defp nonempty?(value), do: is_binary(value) and byte_size(value) > 0
  defp valid_datetime?(%DateTime{}), do: true
  defp valid_datetime?(value) when is_binary(value) do
    case DateTime.from_iso8601(value) do
      {:ok, _, _} -> true
      _ -> false
    end
  end
  defp valid_datetime?(_), do: false

  defp new_id(prefix) do
    prefix <> "-" <> (:crypto.strong_rand_bytes(12) |> Base.url_encode64(padding: false))
  end
end
