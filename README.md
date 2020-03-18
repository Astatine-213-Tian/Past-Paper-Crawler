# Past-Paper-Crawler
A crawler that can help you download CIE past paper from GCE guide.



# To do

* Sort paper by year
* Automatically check for update
* Allow multiple selection in filter
* Automatically update the cache
* Skip downloaded file
* Allow option - create folder for each type of paper

# Update log

## v 1.3

### 1.3.0

- [New Function] Add preference frame - allow user to remove the cache
- [New Function] Add preference frame - allow user to set default download route
- [New Function] Add about us

## v 1.2

### 1.2.3

- [Bug Fixed] Inhibit multiple same frames to open at the same time
- [Bug Fixed] Fixed some arrangement issues on windows
- [Bug Fixed] Fixed the issue that when selecting the individual file mode then changing the subject, the display mode will not change while the selection is initialized to pair mode
- [Bug Fixed] Fixed the issue of not pairing all papers in pair mode

### 1.2.2

- [New Function] Cache subject and paper list information in local file
- [Enhancement] Solve the low resolution issue for compiled file
- [New Function] Add a logo

### 1.2.1

- [Bugs fixed]
  - Prevent hiding type filter when switching back to pair mode
  - Inhibit chose of style before paper finished loading
- [Enhancement] Increase filter's speed
- [Enhancement] Add "Paper" and "Region" for hint in the filter
- [Enhancement] Make RetryFrame always float on the top

### 1.2.0

- [Enhancement] Reconstruct GUI by using BoxSizer
- [New Function] Allow filtering individual by paper type - qp, ms, er ....
- [Enhancement] Merger win and mac version into one file

## v 1.1

### 1.1.1

- [Bugs fixed] Reset the paper list when switching subjects / levels

### 1.1.0

- [New Function] Add progress bar
- [New Function] Allow download to be cancelled

## v 1.0

### 1.0

- Implement crawler module (source - GCE guide)
- Implement GUI
  - Allow filtering paper by subject, season, paper number, region
  - Select All paper and download
- Implement multitasking when downloading