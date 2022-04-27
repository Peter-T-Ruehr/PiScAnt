library(filesstrings)
library(stringr)

RAW_folder <- "C:/Users/peter/Documents/projects/scAnt/scAnt-master/PR_2097_Phyllium_philippinicum/RAW"
file.list <- list.files(RAW_folder, pattern = "_\\.jpg")

folder_names <- gsub("_step_.+$", "", file.list)
folder_names <- unique(folder_names)

for(i in 1:length(folder_names)){
  curr.folder.name <- folder_names[i]
  curr.image.files <- file.list[grepl(curr.folder.name, file.list)]
  
  dir.create(file.path(RAW_folder, curr.folder.name))
  
  for(j in 1:length(curr.image.files)){
    curr.image <- curr.image.files[j]
    file.move(file.path(RAW_folder, curr.image), file.path(RAW_folder, curr.folder.name)) # , paste0(str_pad(j, 3, pad = "0"), ".jpg"))
  }
  print(round(i*100/length(folder_names), 2))
}




x_min = 0
x_step = 30
x_max = 330

y_min = 0
y_step = 80
y_max = 1600

z_min = 500
z_step = 500
z_max = 7500

steps_x = ceiling((x_max - x_min) / x_step)
steps_x

steps_y = ceiling((y_max - y_min) / y_step)
steps_y

steps_z = ceiling((z_max - z_min) / z_step)
steps_z

steps_all = steps_x * steps_y * steps_z
steps_all
