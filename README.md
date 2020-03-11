**How to work on a task:**

 create a new branch
 
 `>git checkout -b branch_name`
 
or switch to existing branch

`>git checkout branch_name`

make your changes.....

add your changes to local repo

`>git add path_to_file_or_folder (. for current)`

commit your changes to local repo, message is required

`>git commit -m "commit message"`

push your changes to remote repo

`>git push origin branch_name`

go to github to your branch and open PR (pull request)

after at least one +1 you can merge your PR to upstream

**How to update master:**

`>git checkout master`

`>git pull upstream master`

`>git push origin master`

`>git checkout branch_name`

`>git rebase master`
