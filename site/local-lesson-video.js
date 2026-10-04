(() => {
  const video = document.getElementById('lesson-video');
  const input = document.getElementById('local-video-file');
  const reset = document.getElementById('reset-lesson-video');
  const status = document.getElementById('local-video-status');
  const warning = document.getElementById('local-video-warning');
  const suppliedNote = document.getElementById('supplied-video-note');
  const track = document.getElementById('lesson-captions');
  let supplied = null;
  let localUrl = null;

  input.addEventListener('change', () => {
    const file = input.files[0];
    input.value = '';
    if (!file) return;
    if (!file.size || (file.type && !file.type.startsWith('video/'))) {
      status.textContent = 'Unable to open this file. Choose a non-empty video file.';
      return;
    }
    if (!supplied) {
      const src = video.getAttribute('src');
      if (!src) {
        status.textContent = 'Unable to select local video before the lesson loads. Try again when it is ready.';
        return;
      }
      supplied = {src, track, mode: track.track.mode, default: track.default,
        label: video.getAttribute('aria-label')};
    }
    const nextUrl = URL.createObjectURL(file);
    video.pause();
    supplied.track.track.mode = 'disabled';
    supplied.track.default = false;
    supplied.track.remove();
    const previousUrl = localUrl;
    localUrl = nextUrl;
    video.src = localUrl;
    video.setAttribute('aria-label', 'Selected local video');
    video.load();
    if (previousUrl) URL.revokeObjectURL(previousUrl);
    reset.disabled = false;
    suppliedNote.hidden = true;
    warning.hidden = false;
    status.textContent = `Local video: ${file.name}. No upload. Reloading requires selecting it again.`;
  });

  reset.addEventListener('click', () => {
    if (!localUrl) return;
    video.pause();
    const previousUrl = localUrl;
    localUrl = null;
    video.src = supplied.src;
    video.setAttribute('aria-label', supplied.label);
    supplied.track.default = supplied.default;
    video.prepend(supplied.track);
    video.load();
    supplied.track.track.mode = supplied.mode;
    URL.revokeObjectURL(previousUrl);
    reset.disabled = true;
    suppliedNote.hidden = false;
    warning.hidden = true;
    status.textContent = 'Supplied video and captions restored.';
  });

  video.addEventListener('error', () => {
    if (localUrl) {
      status.textContent = 'Unable to play this local video. The file may be damaged or its codec unsupported. Choose another video or restore the supplied video.';
    }
  });

  window.addEventListener('pagehide', event => {
    if (!event.persisted && localUrl) URL.revokeObjectURL(localUrl);
  });
})();
