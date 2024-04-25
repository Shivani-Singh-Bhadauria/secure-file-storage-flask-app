function deleteFile(fileId) {
  fetch("/delete-file", {
    method: "POST",
    body: JSON.stringify({ fileId: fileId }),
  }).then((_res) => {

  });
}

function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}







