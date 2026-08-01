const folderDatabase = new DB("Music7", 1, {
    InputFolderPath: "id",
});

const FOLDER_STORE = "InputFolderPath";
let selectedFolderHandle = null;

function setFolderStatus(message) {
    loadStatus.textContent = message;
}

async function useFolder(folder) {
    const permission = await folder.handle.queryPermission({ mode: "read" });
    const granted = permission === "granted" ||
        (permission === "prompt" && await folder.handle.requestPermission({ mode: "read" }) === "granted");

    if (!granted) {
        setFolderStatus(`Folder access was not allowed: ${folder.name}`);
        return;
    }

    selectedFolderHandle = folder.handle;
    selectFolderE.textContent = folder.name;
    setFolderStatus(`Selected folder: ${folder.name}`);
    selectFolderDialog.close();
}

async function showRegisteredFolders() {
    const folders = await folderDatabase.getAll(FOLDER_STORE);
    registeredFolderList.replaceChildren();

    if (folders.length === 0) {
        registeredFolderList.textContent = "No registered folders.";
        return;
    }

    folders
        .sort((a, b) => b.updatedAt - a.updatedAt)
        .forEach((folder) => {
            const button = document.createElement("button");
            button.type = "button";
            button.textContent = folder.name;
            button.addEventListener("click", () => useFolder(folder));
            registeredFolderList.append(button);
        });
}

async function chooseFolderFromPicker() {
    try {
        const handle = await window.showDirectoryPicker();
        const folder = {
            id: crypto.randomUUID(),
            handle,
            name: handle.name,
            updatedAt: Date.now(),
        };

        await folderDatabase.save(FOLDER_STORE, folder);
        await useFolder(folder);
    } catch (error) {
        if (error.name !== "AbortError") {
            console.error("Unable to select folder:", error);
            setFolderStatus("Unable to select folder.");
        }
    }
}

async function openFolderDialog() {
    try {
        await showRegisteredFolders();
        selectFolderDialog.showModal();
    } catch (error) {
        console.error("Unable to read registered folders:", error);
        setFolderStatus("Unable to read registered folders.");
    }
}

function startLoad() {
    if (!selectedFolderHandle) {
        setFolderStatus("Select a folder to start.");
        openFolderDialog();
        return;
    }

    // Loading the selected folder is implemented by the playback workflow.
}

load.addEventListener("click", startLoad);
selectFolderE.addEventListener("click", openFolderDialog);
selectFolderFromDb.addEventListener("click", showRegisteredFolders);
selectFolderFromPicker.addEventListener("click", chooseFolderFromPicker);
cancelSelectFolder.addEventListener("click", () => selectFolderDialog.close());
