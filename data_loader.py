import torch
import torch.utils.data
import numpy as np


# reads the binary file and return the data in ascii format
def _read_binary_file(fname, dim):
    with open(fname, 'rb') as fid:
        data = np.fromfile(fid, dtype=np.float32)
    assert data.shape[0] % dim == 0.0
    data = data.reshape(-1, dim)
    data = data.T
    return data, data.shape[1]

class LoadDataset(torch.utils.data.Dataset):
    """
    Custom dataset compatible with torch.utils.data.DataLoader
    """
    def __init__(self, x_files_list, y_files_list, in_dim, out_dim):
        """Set the path for data

        Args:
            x_files_list: list of input files with full path
            y_files_list: list of target files with full path
            x_dim: input dimension
            y_dim: output dimension
        """
        self.x_files_list = x_files_list
        self.y_files_list = y_files_list
        self.in_dim = in_dim
        self.out_dim = out_dim
        assert len(x_files_list) == len(y_files_list)
        
    def __getitem__(self, index):
        """Returns one data pair (x_data, y_data)."""
        x_file = self.x_files_list[index]
        y_file = self.y_files_list[index]

        x_data, no_frames_x = _read_binary_file(x_file, self.in_dim)
        y_data, no_frames_y = _read_binary_file(y_file, self.out_dim)

        assert (no_frames_x == no_frames_y)
        x_data = x_data.reshape(1,self.in_dim, no_frames_x)
        y_data = y_data.reshape(1,self.out_dim, no_frames_y)

        return (torch.FloatTensor(x_data), torch.FloatTensor(y_data))
    
    def __len__(self):
        return len(self.x_files_list)

def get_loader(x_files_list, y_files_list, in_dim, out_dim, batch_size,
               shuffle, num_workers):
    # Custom dataset
    data = LoadDataset(x_files_list=x_files_list,
                    y_files_list=y_files_list,
                    in_dim=in_dim,
                    out_dim=out_dim)
    
    # Data loader
    # This will return (x_data, y_data) for every iteration
    # x_data: tensor of shape (batch_size, in_dim)
    # y_data: tensor of shape (batch_size, out_dim)
    sampler = torch.utils.data.sampler.RandomSampler(data)
    data_loader = torch.utils.data.DataLoader(dataset=data,
                                              batch_size=batch_size,
                                              sampler=sampler,
                                              num_workers=num_workers)
    return data_loader


if __name__ == "__main__":
    x_files_list_file = '/work/t405/T40521/shared/vocomp/nick/straight/ref_files.list'
    y_files_list_file = '/work/t405/T40521/shared/vocomp/nick/straight/gen_files.list' 
    in_dim = 60
    out_dim = 60
    batch_size = 1
    with open(x_files_list_file, 'r') as fid:
        x_files_list = [l.strip() for l in fid.readlines()]

    with open(y_files_list_file, 'r') as fid:
        y_files_list = [l.strip() for l in fid.readlines()]
    
    x_files_list = x_files_list[0:len(y_files_list)]

    data_loader = get_loader(x_files_list, y_files_list, 
                            in_dim, out_dim, batch_size, False, 3)
    for _ in range(1):
        for i, (x_data, y_data) in enumerate(data_loader):
            print i, x_data.size(), y_data.size()
