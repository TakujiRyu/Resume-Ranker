document.addEventListener('DOMContentLoaded', () => {
    const sortSelect = document.getElementById('sortSelect');
    const exportBtn = document.getElementById('exportBtn');
    const resultsBody = document.getElementById('resultsBody');
    const searchInput = document.getElementById('searchInput');
    const noResults = document.getElementById('noResults');

    // Helper function to get education rank
    function educationRank(edu) {
        if (!edu) return 0;
        edu = edu.toLowerCase();
        if (edu.includes('phd') || edu.includes('doctorate')) return 3;
        if (edu.includes('master') || edu.match(/m\.?s\.?|m\.?a\.?/)) return 2;
        if (edu.includes('bachelor') || edu.match(/b\.?s\.?|b\.?a\.?/)) return 1;
        return 0;
    }

    // Parse experience text to extract years (simple)
    function parseExperience(expCell) {
        let totalYears = 0;
        const lis = expCell.querySelectorAll('li');
        lis.forEach(li => {
            const match = li.textContent.match(/(\d+)/);
            if (match) totalYears += parseInt(match[1]);
        });
        return totalYears;
    }

    // Sort table rows based on selected criteria
    function sortResults() {
        const sortBy = sortSelect.value;
        const rows = Array.from(resultsBody.querySelectorAll('tr'));

        rows.sort((a, b) => {
            if (sortBy === 'score') {
                const scoreA = parseFloat(a.cells[2].textContent) || 0;
                const scoreB = parseFloat(b.cells[2].textContent) || 0;
                return scoreB - scoreA;
            } else if (sortBy === 'education') {
                const eduA = educationRank(a.cells[4].textContent);
                const eduB = educationRank(b.cells[4].textContent);
                return eduB - eduA;
            }
            return 0;
        });

        rows.forEach((row, idx) => {
            row.cells[0].textContent = idx + 1;
            resultsBody.appendChild(row);
        });
    }

    // Export table data as CSV
    function exportResults() {
        const rows = Array.from(resultsBody.querySelectorAll('tr')).filter(row => row.style.display !== 'none');
        if (rows.length === 0) {
            alert('No results to export');
            return;
        }

        const csvHeaders = ['Rank', 'Name', 'Score', 'Experience', 'Qualifications', 'Skills', 'Status'];
        let csvContent = csvHeaders.join(',') + '\n';

        rows.forEach(row => {
            const cols = row.querySelectorAll('td');
            const rank = cols[0].textContent.trim();
            const name = `"${cols[1].textContent.trim()}"`;
            const score = cols[2].textContent.trim();
            
            const expLis = cols[3].querySelectorAll('li');
            const experience = Array.from(expLis).map(li => li.textContent.trim()).join('; ');

            const education = `"${cols[4].textContent.trim()}"`;
            const skills = `"${cols[5].textContent.trim()}"`;
            const status = `"${cols[6].textContent.trim()}"`;

            const csvRow = [rank, name, score, `"${experience}"`, education, skills, status].join(',');
            csvContent += csvRow + '\n';
        });

        const blob = new Blob([csvContent], {type: 'text/csv'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'resume_rankings.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // Search and filter results by name or skills
    function filterResults() {
        const query = searchInput.value.toLowerCase().trim();
        const rows = Array.from(resultsBody.querySelectorAll('tr'));
        let visibleCount = 0;

        rows.forEach(row => {
            const name = row.cells[1].textContent.toLowerCase();
            const skills = row.cells[5].textContent.toLowerCase();

            if (name.includes(query) || skills.includes(query)) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });

        // Show or hide "No results" message
        if (visibleCount === 0) {
            noResults.style.display = 'block';
        } else {
            noResults.style.display = 'none';
        }
    }

    sortSelect.addEventListener('change', () => {
        sortResults();
        filterResults(); // Keep filtering after sort
    });
    exportBtn.addEventListener('click', exportResults);
    searchInput.addEventListener('input', () => {
        filterResults();
        sortResults(); // Keep sort consistent with filtered results
    });

    // Initial sort to display nicely on load
    sortResults();
});

const uploadBox = document.getElementById('uploadBox');
const resumeInput = document.getElementById('resumeInput');
const fileNamesEl = document.getElementById('fileNames');
const uploadSubmitBtn = document.getElementById('uploadSubmitBtn');

resumeInput.addEventListener('change', (event) => {
    const files = event.target.files;
    const fileNamesEl = document.getElementById('fileNames');

    if (files.length === 0) {
        fileNamesEl.textContent = '';
        uploadSubmitBtn.disabled = true;
    } else if (files.length === 1) {
        fileNamesEl.textContent = `Selected file: ${files[0].name}`;
        uploadSubmitBtn.disabled = false;
    } else {
        fileNamesEl.textContent = `Selected files: ${Array.from(files).map(f => f.name).join(', ')}`;
        uploadSubmitBtn.disabled = false;
    }
});
