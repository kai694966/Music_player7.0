function changeVolume(volarg=undefined) {
    const barVolume = Number(volumeBar.value)/100
    const inputVolume = Number(volumeInput.value)/100
    const checkbox = muteCheckBox.checked

    if (volarg) {
        volumeInput.value = volarg
        volumeBar.value = volarg
    }

    if (muteCheckBox.checked) {
        volumeInput.disabled = true
        volumeBar.disabled = true
    } else {
        volumeInput.disabled = false
        volumeBar.disabled = false
    }

    let isPlaying = undefined
    const vol = Number(volumeBar.value)/100
    const videoM_Display = window.getComputedStyle(videoM).display
    const audioM_Display = window.getComputedStyle(audioM).display
    const videoJ_Display = window.getComputedStyle(videoJ).display
    const audioJ_Display = window.getComputedStyle(audioJ).display

    if (videoM_Display === "block" || audioM_Display === "block" || videoJ_Display == "block" || audioJ_Display == "block") {
        isPlaying = true
    }else {
        isPlaying = false
    }

    const bool = !(isPlaying && !isInSleepMode && !isInStopMode)
    
    //bool:BGMを流すべき時に1

    let bVol =   bool*!checkbox*volume
    let mjVol = !bool*!checkbox*volume
    let seVol =       !checkbox*volume

    audioB.volume = bVol
    videoB.volume = bVol
    audioM.volume = mjVol
    videoM.volume = mjVol
    audioJ.volume = mjVol
    videoJ.volume = mjVol
    audioSE.volume = seVol

    volume.innerText = `BGM:${bVol*100}\nMusic:${mjVol*100}`
}