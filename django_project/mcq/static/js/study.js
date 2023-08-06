function toggleSubList(chapterId) {
    let subList = document.getElementById(chapterId);
    if (subList.style.display === 'none') {
      subList.style.display = 'block';
    } else {
      subList.style.display = 'none';
    }
    let presetName = document.querySelector('a[name="' + chapterId + '"]');
    if (presetName) {
      presetName.scrollIntoView({ behavior: "smooth", block: "start", inline: "nearest"  });
    }
  }