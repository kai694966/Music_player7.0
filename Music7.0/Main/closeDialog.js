    // Close modal dialogs when their backdrop (outside the dialog content) is clicked.
    document.querySelectorAll('dialog').forEach((dialog) => {
        dialog.addEventListener('click', (event) => {
            const bounds = dialog.getBoundingClientRect();
            const clickedOutside =
                event.clientX < bounds.left || event.clientX > bounds.right ||
                event.clientY < bounds.top || event.clientY > bounds.bottom;

            if (clickedOutside) {
                dialog.close();
            }
        });
    });