###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.qsv.util import *
from ....lib.ffmpeg.qsv.vpp import VppTest

spec      = load_test_spec("vpp", "scale")
spec_r2r  = load_test_spec("vpp", "scale", "r2r")

@slash.requires(*platform.have_caps("vpp", "scale"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps    = platform.get_caps("vpp", "scale"),
    )
    super(default, self).before()

  def init(self, tspec, case, scale_width, scale_height, scale_op):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case          = case,
      scale_height  = scale_height,
      scale_width   = scale_width,
      vpp_op        = scale_op,
    )

  @slash.parametrize(*gen_vpp_scale_parameters(spec))
  def test(self, case, scale_width, scale_height, scale_op):
    self.init(spec, case, scale_width, scale_height, scale_op)
    self.vpp()

  @slash.parametrize(*gen_vpp_scale_parameters(spec_r2r))
  def test_r2r(self, case, scale_width, scale_height, scale_op):
    self.init(spec_r2r, case, scale_width, scale_height, scale_op)
    vars(self).setdefault("r2r", 5)
    self.vpp()

  def check_metrics(self):
    check_filesize(
        self.decoded, self.scale_width, self.scale_height,
        self.frames, self.format)

    fmtref = format_value(self.reference, **vars(self))

    ssim = calculate_ssim(
      fmtref, self.decoded,
      self.scale_width, self.scale_height,
      self.frames, self.format)

    get_media()._set_test_details(ssim = ssim)

    assert 1.0 >= ssim[0] >= 0.97
    assert 1.0 >= ssim[1] >= 0.97
    assert 1.0 >= ssim[2] >= 0.97
