(() => {
  const fetchStatus = async (url) => {
    const response = await fetch(url, {
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
    if (!response.ok) throw new Error("party status unavailable");
    return response.json();
  };

  const lobby = document.querySelector("[data-party-lobby]");
  if (lobby) {
    const pollLobby = async () => {
      try {
        const state = await fetchStatus(lobby.dataset.statusUrl);
        const signature = state.members.map((member) => member.id).join(",");
        if (
          state.status !== "waiting" ||
          signature !== lobby.dataset.memberSignature ||
          String(state.host_user_id) !== lobby.dataset.hostUserId ||
          String(state.rounds) !== lobby.dataset.rounds ||
          state.name !== lobby.dataset.lobbyName
        ) {
          window.location.reload();
          return;
        }
      } catch (_) {
        window.location.reload();
        return;
      }
      window.setTimeout(pollLobby, 800);
    };
    window.setTimeout(pollLobby, 800);
  }

  const partyIndex = document.querySelector("[data-party-index]");
  if (partyIndex) {
    const pollPartyIndex = async () => {
      try {
        const state = await fetchStatus(partyIndex.dataset.statusUrl);
        if (state.signature !== partyIndex.dataset.partySignature) {
          window.location.reload();
          return;
        }
      } catch (_) {
        // A brief connection interruption should not throw the player out.
      }
      window.setTimeout(pollPartyIndex, 1500);
    };
    window.setTimeout(pollPartyIndex, 1500);
  }

  const presence = document.querySelector("[data-party-presence]");
  const feedback = document.querySelector("[data-party-feedback-sync]");
  if (presence && !feedback) {
    const sendHeartbeat = async () => {
      try {
        await fetchStatus(presence.dataset.statusUrl);
      } catch (_) {
        window.location.reload();
        return;
      }
      window.setTimeout(sendHeartbeat, 3000);
    };
    window.setTimeout(sendHeartbeat, 3000);
  }

  const countdown = document.querySelector("[data-party-countdown]");
  if (countdown) {
    const initialRemaining = Number(countdown.dataset.remainingMs || 0);
    const visualDuration = Number(countdown.dataset.visualSeconds || 2) * 1000;
    const startedAt = performance.now();
    const number = countdown.querySelector("[data-party-countdown-number]");
    const bar = countdown.querySelector("[data-party-countdown-bar]");

    const draw = () => {
      const remaining = Math.max(0, initialRemaining - (performance.now() - startedAt));
      if (remaining > visualDuration) {
        number.textContent = "…";
        bar.style.width = "0%";
      } else {
        number.textContent = String(Math.max(1, Math.ceil(remaining / 1000)));
        bar.style.width = `${Math.max(0, Math.min(100, (remaining / visualDuration) * 100))}%`;
      }
      if (remaining <= 0) {
        window.location.replace(countdown.dataset.refreshUrl);
        return;
      }
      window.requestAnimationFrame(draw);
    };
    draw();
  }

  if (feedback) {
    const questionIndex = Number(feedback.dataset.questionIndex);
    const minimumFeedbackMs = Number(feedback.dataset.feedbackSeconds || 4) * 1000;
    const nextCountdownMs = Number(feedback.dataset.nextCountdownSeconds || 2) * 1000;
    const feedbackStartedAt = performance.now();
    let redirectScheduled = false;

    const scheduleRedirect = (requestedDelay) => {
      if (redirectScheduled) return;
      redirectScheduled = true;
      const minimumRemaining = Math.max(
        0,
        minimumFeedbackMs - (performance.now() - feedbackStartedAt),
      );
      window.setTimeout(
        () => window.location.replace(feedback.dataset.lobbyUrl),
        Math.max(minimumRemaining, requestedDelay),
      );
    };

    const pollFeedback = async () => {
      try {
        const state = await fetchStatus(feedback.dataset.statusUrl);
        if (state.status === "completed") {
          scheduleRedirect(Number(state.completion_feedback_remaining_ms || 0));
          return;
        }
        if (Number(state.current_question_index) > questionIndex) {
          const untilCountdown = Math.max(
            0,
            Number(state.question_starts_in_ms || 0) - nextCountdownMs,
          );
          scheduleRedirect(untilCountdown);
          return;
        }
      } catch (_) {
        scheduleRedirect(0);
        return;
      }
      window.setTimeout(pollFeedback, 650);
    };
    pollFeedback();
  }
})();
