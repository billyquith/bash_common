# Xcode command-line helpers

# Delete derived data. Good to do occasionally.
function ddd
{
  local DERIVED=~/Library/Developer/Xcode/DerivedData    
  pushd $DERIVED
  echo In $(pwd)
  
  du -ch -d1 .
    
  if [ "$1" == "-f" ]; then      
    #Sometimes, 1 file remains, so loop until no files remain
    local numRemainingFiles=1
    while [ $numRemainingFiles -gt 0 ]; do
      #Delete the files, recursively
      rm -rf *
  
      #Update file count
      numRemainingFiles=`ls | wc -l`
    done
  else
    rm -rf *  # !!!
  fi

  popd
  echo Done
}
